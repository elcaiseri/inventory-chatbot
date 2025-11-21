from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, condecimal, conint, constr

# Constrained types matching column sizes
Code50 = constr(max_length=50)
Code100 = constr(max_length=100)
Name200 = constr(max_length=200)
City100 = constr(max_length=100)
Country100 = constr(max_length=100)
Phone50 = constr(max_length=50)
Currency10 = constr(max_length=10)
Status30 = constr(max_length=30)

Dec18_2 = condecimal(max_digits=18, decimal_places=2)
Dec18_4 = condecimal(max_digits=18, decimal_places=4)


class AssetStatus(str, Enum):
    ACTIVE = "Active"
    IN_REPAIR = "InRepair"
    DISPOSED = "Disposed"


class BillStatus(str, Enum):
    OPEN = "Open"
    PAID = "Paid"
    VOID = "Void"


class POStatus(str, Enum):
    OPEN = "Open"
    APPROVED = "Approved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class SOStatus(str, Enum):
    OPEN = "Open"
    SHIPPED = "Shipped"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class TxnType(str, Enum):
    MOVE = "Move"
    ADJUST = "Adjust"
    DISPOSE = "Dispose"
    CREATE = "Create"


# Base config model
class ORMModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # replaces orm_mode
        validate_by_name=True,  # replaces allow_population_by_field_name
        populate_by_name=True,  # allow passing field names as well as aliases
    )


class EnumValueModel(ORMModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class Customer(ORMModel):
    customer_id: Optional[int] = Field(None, alias="CustomerId")
    customer_code: Code50 = Field(..., alias="CustomerCode")
    customer_name: Name200 = Field(..., alias="CustomerName")
    email: Optional[constr(max_length=200)] = Field(None, alias="Email")
    phone: Optional[Phone50] = Field(None, alias="Phone")
    billing_address1: Optional[constr(max_length=200)] = Field(
        None, alias="BillingAddress1"
    )
    billing_city: Optional[City100] = Field(None, alias="BillingCity")
    billing_country: Optional[Country100] = Field(None, alias="BillingCountry")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    is_active: bool = Field(True, alias="IsActive")


class Vendor(ORMModel):
    vendor_id: Optional[int] = Field(None, alias="VendorId")
    vendor_code: Code50 = Field(..., alias="VendorCode")
    vendor_name: Name200 = Field(..., alias="VendorName")
    email: Optional[constr(max_length=200)] = Field(None, alias="Email")
    phone: Optional[Phone50] = Field(None, alias="Phone")
    address_line1: Optional[constr(max_length=200)] = Field(None, alias="AddressLine1")
    city: Optional[City100] = Field(None, alias="City")
    country: Optional[Country100] = Field(None, alias="Country")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    is_active: bool = Field(True, alias="IsActive")


class Site(ORMModel):
    site_id: Optional[int] = Field(None, alias="SiteId")
    site_code: Code50 = Field(..., alias="SiteCode")
    site_name: Name200 = Field(..., alias="SiteName")
    address_line1: Optional[constr(max_length=200)] = Field(None, alias="AddressLine1")
    city: Optional[City100] = Field(None, alias="City")
    country: Optional[Country100] = Field(None, alias="Country")
    time_zone: Optional[constr(max_length=100)] = Field(None, alias="TimeZone")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    is_active: bool = Field(True, alias="IsActive")


class Location(ORMModel):
    location_id: Optional[int] = Field(None, alias="LocationId")
    site_id: int = Field(..., alias="SiteId")
    location_code: Code50 = Field(..., alias="LocationCode")
    location_name: Name200 = Field(..., alias="LocationName")
    parent_location_id: Optional[int] = Field(None, alias="ParentLocationId")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    is_active: bool = Field(True, alias="IsActive")


class Item(ORMModel):
    item_id: Optional[int] = Field(None, alias="ItemId")
    item_code: Code100 = Field(..., alias="ItemCode")
    item_name: Name200 = Field(..., alias="ItemName")
    category: Optional[constr(max_length=100)] = Field(None, alias="Category")
    unit_of_measure: Optional[constr(max_length=50)] = Field(
        None, alias="UnitOfMeasure"
    )
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")
    is_active: bool = Field(True, alias="IsActive")


class Asset(EnumValueModel):
    asset_id: Optional[int] = Field(None, alias="AssetId")
    asset_tag: Code100 = Field(..., alias="AssetTag")
    asset_name: Name200 = Field(..., alias="AssetName")
    site_id: int = Field(..., alias="SiteId")
    location_id: Optional[int] = Field(None, alias="LocationId")
    serial_number: Optional[constr(max_length=200)] = Field(None, alias="SerialNumber")
    category: Optional[constr(max_length=100)] = Field(None, alias="Category")
    status: AssetStatus = Field(AssetStatus.ACTIVE, alias="Status")
    cost: Optional[Dec18_2] = Field(None, alias="Cost")
    purchase_date: Optional[date] = Field(None, alias="PurchaseDate")
    vendor_id: Optional[int] = Field(None, alias="VendorId")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")


class Bill(EnumValueModel):
    bill_id: Optional[int] = Field(None, alias="BillId")
    vendor_id: int = Field(..., alias="VendorId")
    bill_number: Code100 = Field(..., alias="BillNumber")
    bill_date: date = Field(..., alias="BillDate")
    due_date: Optional[date] = Field(None, alias="DueDate")
    total_amount: Dec18_2 = Field(..., alias="TotalAmount")
    currency: Currency10 = Field("USD", alias="Currency")
    status: BillStatus = Field(BillStatus.OPEN, alias="Status")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")


class PurchaseOrder(EnumValueModel):
    po_id: Optional[int] = Field(None, alias="POId")
    po_number: Code100 = Field(..., alias="PONumber")
    vendor_id: int = Field(..., alias="VendorId")
    po_date: date = Field(..., alias="PODate")
    status: POStatus = Field(POStatus.OPEN, alias="Status")
    site_id: Optional[int] = Field(None, alias="SiteId")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")


class PurchaseOrderLine(ORMModel):
    po_line_id: Optional[int] = Field(None, alias="POLineId")
    po_id: int = Field(..., alias="POId")
    line_number: int = Field(..., alias="LineNumber")
    item_id: Optional[int] = Field(None, alias="ItemId")
    item_code: Code100 = Field(..., alias="ItemCode")
    description: Optional[constr(max_length=200)] = Field(None, alias="Description")
    quantity: Dec18_4 = Field(..., alias="Quantity")
    unit_price: Dec18_4 = Field(..., alias="UnitPrice")


class SalesOrder(EnumValueModel):
    so_id: Optional[int] = Field(None, alias="SOId")
    so_number: Code100 = Field(..., alias="SONumber")
    customer_id: int = Field(..., alias="CustomerId")
    so_date: date = Field(..., alias="SODate")
    status: SOStatus = Field(SOStatus.OPEN, alias="Status")
    site_id: Optional[int] = Field(None, alias="SiteId")
    created_at: Optional[datetime] = Field(None, alias="CreatedAt")
    updated_at: Optional[datetime] = Field(None, alias="UpdatedAt")


class SalesOrderLine(ORMModel):
    so_line_id: Optional[int] = Field(None, alias="SOLineId")
    so_id: int = Field(..., alias="SOId")
    line_number: int = Field(..., alias="LineNumber")
    item_id: Optional[int] = Field(None, alias="ItemId")
    item_code: Code100 = Field(..., alias="ItemCode")
    description: Optional[constr(max_length=200)] = Field(None, alias="Description")
    quantity: Dec18_4 = Field(..., alias="Quantity")
    unit_price: Dec18_4 = Field(..., alias="UnitPrice")


class AssetTransaction(EnumValueModel):
    asset_txn_id: Optional[int] = Field(None, alias="AssetTxnId")
    asset_id: int = Field(..., alias="AssetId")
    from_location_id: Optional[int] = Field(None, alias="FromLocationId")
    to_location_id: Optional[int] = Field(None, alias="ToLocationId")
    txn_type: TxnType = Field(..., alias="TxnType")
    quantity: conint(gt=0) = Field(1, alias="Quantity")
    txn_date: Optional[datetime] = Field(None, alias="TxnDate")
    note: Optional[constr(max_length=500)] = Field(None, alias="Note")
