# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::

    $Repo: fastapi_messaging
  $Author: Anders Wiklund
    $Date: 2024-03-24 19:33:51
     $Rev: 72
"""

# BUILTIN modules
from enum import Enum
from uuid import UUID
from datetime import datetime, UTC
from typing import Optional, Callable, List

# Third party modules
from uuid_extensions import uuid7
from pydantic import (BaseModel, ConfigDict,
                      Field, conlist, PositiveInt)

# Local modules
from .documentation import (order_documentation as order_doc)


# ---------------------------------------------------------
#
def utcnow():
    """ Return the current datetime with a UTC timezone.

    :return: Current UTC datetime.
    """
    return datetime.now(UTC)


# ---------------------------------------------------------
#
# noinspection IncorrectFormatting
class Status(str, Enum):
    """ Order status changes.

    CREA -> PAID/FAIL -> DISC -> DRAV -> SHED -> COOK -> PROD -> PICK -> TRAN -> DONE

    An Order can be canceled before DRAV status has been reached (finding an available
    driver sometimes takes time, so the Customer is unwilling to wait any longer).


    :ivar CREA: OrderService state.
    :ivar ORCA: OrderService state.
    :ivar PAID: PaymentService state.
    :ivar REIM: PaymentService state.
    :ivar FAIL: PaymentService state.
    :ivar DESC: DeliveryService state.
    :ivar DRAV: DeliveryService state.
    :ivar SHED: KitchenService state.
    :ivar COOK: KitchenService state.
    :ivar PROD: KitchenService state.
    :ivar PICK: KitchenService state.
    :ivar TRAN: DeliveryService state.
    :ivar DONE: DeliveryService state.
    """
    CREA = 'created'
    ORCA = 'orderCancelled'
    PAID = 'paymentPaid'
    REIM = 'reimbursed'
    FAIL = 'paymentFailed'
    DESC = 'deliveryScheduled'
    DRAV = 'driverAvailable'
    SHED = 'cookingScheduled'
    COOK = 'cookingMeal'
    PROD = 'cookingDone'
    PICK = 'pickedUp'
    TRAN = 'inTransit'
    DONE = 'delivered'


# ---------------------------------------------------------
#
class Products(str, Enum):
    """ Representation of valid products in the system.

    :ivar lasagna: Food product.
    :ivar cheese_burger: Food product.
    :ivar veil: Food product.
    :ivar vego_salad: Food product.
    """
    lasagna = 'Lasagna'
    cheese_burger = 'Double Cheeseburger'
    veil = 'Veil with glazed onions and blue cheese'
    vego_salad = 'Vegetarian Salad with healthy produce'


class OrderItem(BaseModel):
    """ Required order item parameters.


    :ivar product: Ordered product.
    :ivar quantity: Product quantity.
    """
    product: Products
    quantity: PositiveInt = 1


class OrderItems(BaseModel):
    """ A list of the ordered items.


    :ivar items: List of ordered items.
    """
    items: conlist(OrderItem, min_length=1)


# ------------------------------------------------------------------------
#
class MongoBase(BaseModel):
    """
    Class that handles conversions between MongoDB '_id' key
    and our own 'id' key.

    MongoDB uses ``_id`` as an internal default index key.
    We can use that to our advantage.

    :ivar model_config: MongoBase config items.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict) -> Callable:
        """ Convert "_id" (str object) into "id" (UUID object).

        :param data: Current BaseModel object.
        """

        if not data:
            return data

        mongo_id = data.pop('_id', None)
        return cls(**dict(data, id=mongo_id))

    def to_mongo(self, **kwargs: dict) -> dict:
        """ Convert "id" (UUID object) into "_id" (str object).

        :param kwargs: Current BaseModel object parameters.
        """
        parsed = self.model_dump(**kwargs)

        if '_id' not in parsed and 'id' in parsed:
            parsed['_id'] = str(parsed.pop('id'))

        return parsed


# ---------------------------------------------------------
#
class StateUpdateSchema(BaseModel):
    """ Representation of an Order status history in the system.

    :ivar status: Current order status.
    :ivar when: Datetime for updated item(s).
    """
    status: Status = Field(**order_doc['status'])
    when: datetime = Field(default_factory=utcnow, **order_doc['when'])


class OrderUpdateModel(MongoBase):
    """ Representation of an Order in the system.

    :ivar items: List of ordered items.
    :ivar customer_id: Customer identity.
    :ivar kitchen_id: Kitchen identity.
    :ivar delivery_id: Delivery identity.
    :ivar status: Current order status.
    :ivar updated: Datetime for updated order.
    :ivar created: Datetime for created order.
    """
    items: conlist(OrderItem, min_length=1)
    customer_id: UUID = Field(**order_doc['customer_id'])
    kitchen_id: Optional[UUID] = Field(**order_doc['kitchen_id'])
    delivery_id: Optional[UUID] = Field(**order_doc['delivery_id'])
    status: Status = Field(default=Status.CREA, **order_doc['status'])
    updated: Optional[List[StateUpdateSchema]] = Field(**order_doc['updated'])
    created: datetime = Field(default_factory=utcnow, **order_doc['created'])


class OrderModel(OrderUpdateModel):
    """ Representation of an Order in the system.

    :ivar id: Order identity.
    """
    id: UUID = Field(default_factory=uuid7)


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
        for key, value in payload.model_dump().items()}
