# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2023-04-01 17:51:19
     $Rev: 55
"""

# BUILTIN modules
from enum import Enum
from uuid import uuid4
from datetime import datetime
from typing import Optional, Callable, List

# Third party modules
from pydantic import (BaseModel, BaseConfig,
                      Field, UUID4, conlist, conint)

# Local modules
from .documentation import (order_documentation as order_doc)


# ---------------------------------------------------------
#
class Status(str, Enum):
    """ Order status changes.

    CREA -> PAID/FAIL -> DISC -> DRAV -> SHED -> COOK -> PROD -> PICK -> TRAN -> DONE

    An Order can be cancelled before DRAV status has been reached (finding an available
    driver sometimes take time, so the Customer is unwilling to wait any longer).
    """
    CREA = 'created'            # OrderService
    ORCA = 'orderCancelled'     # OrderService
    PAID = 'paymentPaid'        # PaymentService
    REIM = 'reimbursed'         # PaymentService
    FAIL = 'paymentFailed'      # PaymentService
    DESC = 'deliveryScheduled'  # DeliveryService
    DRAV = 'driverAvailable'    # DeliveryService
    SHED = 'cookingScheduled'   # KitchenService
    COOK = 'cookingMeal'        # KitchenService
    PROD = 'cookingDone'        # KitchenService
    PICK = 'pickedUp'           # KitchenService
    TRAN = 'inTransit'          # DeliveryService
    DONE = 'delivered'          # DeliveryService


# ---------------------------------------------------------
#
class Products(str, Enum):
    """ Representation of valid products in the system. """
    lasagna = 'Lasagna'
    cheese_burger = 'Double Cheeseburger'
    veil = 'Veil with glazed onions and blue cheese'
    vego_salad = 'Vegetarian Salad with healthy produce'


class OrderItem(BaseModel):
    """ Required order item parameters. """
    product: Products
    quantity: Optional[conint(ge=1, strict=True)] = 1


class OrderItems(BaseModel):
    """ A list of the ordered items. """
    items: conlist(OrderItem, min_items=1)


# ------------------------------------------------------------------------
#
class MongoBase(BaseModel):
    """
    Class that handles conversions between MongoDB '_id' key
    and our own 'id' key.

    MongoDB uses `_id` as an internal default index key.
    We can use that to our advantage.
    """

    class Config(BaseConfig):
        """ basic config. """
        orm_mode = True
        allow_population_by_field_name = True

    # noinspection PyArgumentList
    @classmethod
    def from_mongo(cls, data: dict) -> Callable:
        """ Convert "_id" (str object) into "id" (UUID object). """

        if not data:
            return data

        mongo_id = data.pop('_id', None)
        return cls(**dict(data, id=mongo_id))

    def to_mongo(self, **kwargs) -> dict:
        """ Convert "id" (UUID object) into "_id" (str object). """
        parsed = self.dict(**kwargs)

        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = str(parsed.pop('id'))

        return parsed


# ---------------------------------------------------------
#
class StateUpdateSchema(BaseModel):
    """ Representation of an Order status history in the system. """
    status: Status = Field(**order_doc['status'])
    when: datetime = Field(default_factory=datetime.utcnow, **order_doc['when'])


class OrderUpdateModel(MongoBase):
    """ Representation of an Order in the system. """
    items: conlist(OrderItem, min_items=1)
    customer_id: UUID4 = Field(**order_doc['customer_id'])
    kitchen_id: Optional[UUID4] = Field(**order_doc['kitchen_id'])
    delivery_id: Optional[UUID4] = Field(**order_doc['delivery_id'])
    status: Status = Field(default=Status.CREA, **order_doc['status'])
    updated: Optional[List[StateUpdateSchema]] = Field(**order_doc['updated'])
    created: datetime = Field(default_factory=datetime.utcnow, **order_doc['created'])


class OrderModel(OrderUpdateModel):
    """ Representation of an Order in the system. """
    id: UUID4 = Field(default_factory=uuid4)


# ---------------------------------------------------------
#
def dict_of(payload: OrderModel) -> dict:
    """  Return a dict representation of an OrderModel that json.dumps will accept.

    All datatime and UUID objects are converted to str.

    :param payload: Current Order object.
    :return: Serializable dict representation of an Order.
    """

    return {
        key: (
            # This row converts datetime values to str within a list of dicts.
            list(map(lambda elem: {'status': elem['status'],
                                   'when': str(elem['when'])}, value))
            if key == 'updated'

            # This row handles values that don't need a conversion.
            else value if key in {'items', 'status'}

            # This row converts all base (not in a structure) UUID and datetime values to str.
            else str(value) if value else None)

        # Iterate over all elements in the payload.
        for key, value in payload.dict().items()}
