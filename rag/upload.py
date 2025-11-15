from fastapi import APIRouter, Request
router = APIRouter()

@router.get("/init")
async def inport_regint():
#add_document ("regint.pdf")
 #   add_document ("regsub.pdf")

    return {"ok": True}