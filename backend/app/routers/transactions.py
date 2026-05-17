# backend/app/routers/transactions.py
import os
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from app.db.pool import get_pool

router = APIRouter()

DEFAULT_INV_ID = os.getenv(
    "DEFAULT_INVESTIGATOR_ID", "11111111-0000-0000-0000-000000000001"
)


# ── GET /api/transactions ────────────────────────────────────
@router.get("/")
async def get_transactions(
    status: Optional[str] = None,
    model_source: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    search: Optional[str] = None,
    pool=Depends(get_pool),
):
    try:
        where, params, i = [], [], 1

        if status:
            where.append(f"t.status = ${i}")
            params.append(status); i += 1
        if model_source:
            where.append(f"t.model_source = ${i}")
            params.append(model_source); i += 1
        if min_score is not None:
            where.append(f"t.ensemble_score >= ${i}")
            params.append(min_score); i += 1
        if max_score is not None:
            where.append(f"t.ensemble_score <= ${i}")
            params.append(max_score); i += 1
        if search:
            where.append(
                f"(t.transaction_ref ILIKE ${i} OR t.location ILIKE ${i} "
                f"OR CAST(t.amount AS TEXT) ILIKE ${i})"
            )
            params.append(f"%{search}%"); i += 1

        where_clause = ("WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT t.id::text, t.transaction_ref, t.amount, t.currency, t.location,
                   t.merchant, t.device, t.merchant_category, t.account_id,
                   t.model_source, t.if_score, t.lstm_score, t.ensemble_score,
                   t.confidence_score, t.ai_explanation, t.status,
                   t.notes, t.flagged_at,
                   inv.full_name AS reviewed_by_name,
                   t.reviewed_at
            FROM transactions t
            LEFT JOIN investigators inv ON inv.id = t.reviewed_by
            {where_clause}
            ORDER BY t.ensemble_score DESC, t.flagged_at DESC
        """
        rows = await pool.fetch(sql, *params)
        return {"success": True, "data": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── GET /api/transactions/:id ────────────────────────────────
@router.get("/{tx_id}")
async def get_transaction(tx_id: str, pool=Depends(get_pool)):
    try:
        row = await pool.fetchrow(
            """
            SELECT t.*, t.id::text AS id, inv.full_name AS reviewed_by_name
            FROM transactions t
            LEFT JOIN investigators inv ON inv.id = t.reviewed_by
            WHERE t.id::text = $1 OR t.transaction_ref = $1
            """,
            tx_id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"success": True, "data": dict(row)}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── PATCH /api/transactions/:id/action ──────────────────────
class ActionBody(BaseModel):
    action: str
    notes: Optional[str] = None
    investigator_id: Optional[str] = None


@router.patch("/{tx_id}/action")
async def take_action(tx_id: str, body: ActionBody, pool=Depends(get_pool)):
    if body.action not in ("fraud", "cleared", "escalated"):
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Must be fraud | cleared | escalated",
        )

    inv_id = body.investigator_id or DEFAULT_INV_ID

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Fetch transaction (try UUID then ref)
            tx = None
            try:
                tx = await conn.fetchrow(
                    "SELECT * FROM transactions WHERE id = $1::uuid", tx_id
                )
            except Exception:
                pass
            if not tx:
                tx = await conn.fetchrow(
                    "SELECT * FROM transactions WHERE transaction_ref = $1", tx_id
                )
            if not tx:
                raise HTTPException(
                    status_code=404, detail=f"Transaction not found: {tx_id}"
                )

            # Fetch investigator with safe fallback
            inv = await conn.fetchrow(
                "SELECT id::text, full_name, username FROM investigators WHERE id = $1::uuid",
                inv_id,
            )
            inv_full_name = inv["full_name"] if inv else "Sarah Chen"
            inv_username  = inv["username"]  if inv else "sarah.chen"
            inv_uuid      = inv_id  # keep as string for UUID casting below

            # Update transaction
            await conn.execute(
                """
                UPDATE transactions
                SET status = $1, reviewed_by = $2::uuid, reviewed_at = NOW(),
                    notes = $3, updated_at = NOW()
                WHERE id = $4
                """,
                body.action, inv_uuid, body.notes, tx["id"],
            )

            # Audit log
            await conn.execute(
                """
                INSERT INTO audit_log
                  (transaction_id, transaction_ref, investigator_id, investigator_name,
                   action, ensemble_score, notes)
                VALUES ($1, $2, $3::uuid, $4, $5, $6, $7)
                """,
                tx["id"], tx["transaction_ref"], inv_uuid, inv_full_name,
                body.action, tx["ensemble_score"], body.notes,
            )

            # Activity log
            amount = f"{float(tx['amount']):,.2f}"
            short_ref = tx["transaction_ref"].split("-")[-1]
            desc_map = {
                "fraud":     f"{inv_full_name} confirmed fraud: {short_ref} (${amount})",
                "cleared":   f"{inv_full_name} cleared as false positive: {short_ref}",
                "escalated": f"{inv_full_name} escalated for senior review: {short_ref}",
            }
            type_map = {"fraud": "detection", "cleared": "clear", "escalated": "alert"}
            source = str(inv_username or "investigator")[:60]

            await conn.execute(
                "INSERT INTO activity_log (event_type, description, source) VALUES ($1, $2, $3)",
                type_map[body.action], desc_map[body.action], source,
            )

    return {
        "success": True,
        "message": f"Transaction {body.action} successfully",
        "transaction_ref": tx["transaction_ref"],
        "action": body.action,
    }
