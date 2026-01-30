from fastapi import APIRouter
from .staff.router import router as staff_router
from .customer.router import router as customer_router
from .driver.router import router as driver_router

router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(staff_router)
router.include_router(customer_router)
router.include_router(driver_router)