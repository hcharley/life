from django.db import models
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.conf import settings

# This app is structured into roomies, items, and records of payments

class LifeBase(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_last_modified = models.DateTimeField(auto_now=True, editable=False)

    def dollar_amount(self, amount):
        if amount is None:
            return "$0"
        return "$%s" % str(amount)

    class Meta:
        abstract = True


class Roomie(LifeBase):
    """
    Gary, Brian & Charley
    """
    name = models.CharField(max_length=500)
    email_address = models.EmailField(max_length=500)

    @property
    def debts(self):
        return Debt.objects.filter(debtor=self)
    
    @property
    def total_owed(self):
        return sum(debt.amount_still_owed for debt in self.debts)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', )


class Item(LifeBase):
    """
    A record of debt
    """
    name = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=500,decimal_places=2)

    def __unicode__(self):
        return self.name


class Debt(LifeBase):
    """
    A record of debt
    """
    item = models.ForeignKey(Item)
    creditor = models.ForeignKey(Roomie, related_name="+", default=1)
    debtor = models.ForeignKey(Roomie, related_name="+")
    amount = models.DecimalField(max_digits=500,decimal_places=2)

    @property
    def amount_still_owed(self):
        running_amount = self.amount
        for payment in self.payments:
            running_amount = running_amount - payment.amount
        return running_amount

    @property
    def payments(self):
        return Payment.objects.filter(debt=self)

    @property
    def payment_count(self):
        return len(self.payments)

    @property
    def payment_sum(self):
        return sum(payment.amount for payment in self.payments)

    @property
    def paid_percent(self):
        return int((self.payment_sum / self.amount) * 100)

    @property
    def paid_in_full(self):
        return self.amount_still_owed == 0


    def __unicode__(self):
        return "%s's %s owed to %s" % (self.debtor.name, self.item.name, self.creditor.name)


class Payment(LifeBase):
    """
    A record of debt
    """
    debt = models.ForeignKey(Debt)
    amount = models.DecimalField(max_digits=500,decimal_places=2)

    def __unicode__(self):
        return "$%i Payment for %s" % (self.amount, self.debt)



# class Item(LifeBase):
#     """
#     An item that we all buy.
#     """
#     name = models.CharField(max_length=500)
#     total_amount = models.IntegerField()
#     bought_date = models.DateField(auto_now_add=True)

#     def dollar_amount(self, amount=None):
#         if amount is None:
#             amount = self.total_amount
#         return "$%i" % amount

#     def split_up(self):
#         roomie_count = len(Roomie.objects.all())
#         return self.dollar_amount(self.total_amount / roomie_count)


#     def payment(self):
#         return RoomiePaysForItem.objects.get(item=self)

#     def __unicode__(self):
#         return self.name


# class Payment(LifeBase):
#     """
#     A payment from a roomie for something else.
#     """
#     amount = models.IntegerField()
#     roomie = models.ForeignKey(Roomie, related_name="+")

#     form_of_payment = models.CharField(blank=True, max_length=500)

#     note = models.TextField(blank=True)

#     class Meta:
#         abstract = True


# class RoomiePaysRoomie(Payment):
#     """
#     A payment for roomie to roomie.
#     """
#     to_roomie = models.ForeignKey(Roomie, related_name="+")


# class RoomiePaysForItem(Payment):
#     """
#     A payment for an item.
#     """
#     item = models.ForeignKey(Item)

#     def __unicode__(self):
#         return self.name