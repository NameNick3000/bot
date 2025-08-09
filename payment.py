import string
import random
import config
import sqlite3
import aiohttp
import datetime
from yoomoney.operation.operation import Operation


class Client:
    def __init__(
        self,
        token: str = None,
        base_url: str = None
    ):
        if base_url is None:
            self.base_url = "https://yoomoney.ru/api/"
        if token is not None:
            self.token = token

    async def operation_history(
        self,
        label: str = None
    ):
        headers = {
            'Authorization': 'Bearer ' + str(self.token),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {"label": label}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=self.base_url+"operation-history", data=payload, headers=headers
            ) as response:
                data = await response.json()
        operations = list()
        for operation_data in data["operations"]:
            param = {}
            if "operation_id" in operation_data:
                param["operation_id"] = operation_data["operation_id"]
            else:
                param["operation_id"] = None
            if "status" in operation_data:
                param["status"] = operation_data["status"]
            else:
                param["status"] = None
            if "title" in operation_data:
                param["title"] = operation_data["title"]
            else:
                param["title"] = None
            if "pattern_id" in operation_data:
                param["pattern_id"] = operation_data["pattern_id"]
            else:
                param["pattern_id"] = None
            if "direction" in operation_data:
                param["direction"] = operation_data["direction"]
            else:
                param["direction"] = None
            if "amount" in operation_data:
                param["amount"] = operation_data["amount"]
            else:
                param["amount"] = None
            if "label" in operation_data:
                param["label"] = operation_data["label"]
            else:
                param["label"] = None
            if "type" in operation_data:
                param["type"] = operation_data["type"]
            else:
                param["type"] = None

            operation = Operation(
                operation_id=param["operation_id"],
                status=param["status"],
                title=param["title"],
                pattern_id=param["pattern_id"],
                direction=param["direction"],
                amount=param["amount"],
                label=param["label"],
                type=param["type"],
            )
            operations.append(operation)

        return operations


class Quickpay:
    def __init__(
        self,
        receiver: str,
        quickpay_form : str,
        targets: str,
        paymentType: str,
        sum: float,
        formcomment: str = None,
        short_dest: str = None,
        label: str = None,
        comment: str = None,
        successURL: str = None,
        need_fio: bool = None,
        need_email: bool = None,
        need_phone: bool = None,
        need_address: bool = None,
    ):
        self.receiver = receiver
        self.quickpay_form = quickpay_form
        self.targets = targets
        self.paymentType = paymentType
        self.sum = sum
        self.formcomment = formcomment
        self.short_dest = short_dest
        self.label = label
        self.comment = comment
        self.successURL = successURL
        self.need_fio = need_fio
        self.need_email = need_email
        self.need_phone = need_phone
        self.need_address = need_address

        self._request()

    def _request(self):

        self.base_url = "https://yoomoney.ru/quickpay/confirm.xml?"

        payload = {}

        payload["receiver"] = self.receiver
        payload["quickpay_form"] = self.quickpay_form
        payload["targets"] = self.targets
        payload["paymentType"] = self.paymentType
        payload["sum"] = self.sum

        if self.formcomment != None:
            payload["formcomment"] = self.formcomment
        if self.short_dest != None:
            payload["short_dest"] = self.short_dest
        if self.label != None:
            payload["label"] = self.label
        if self.comment != None:
            payload["comment"] = self.comment
        if self.successURL != None:
            payload["successURL"] = self.successURL
        if self.need_fio != None:
            payload["need_fio"] = self.need_fio
        if self.need_email != None:
            payload["need_email"] = self.need_email
        if self.need_phone != None:
            payload["need_phone"] = self.need_phone
        if self.need_address != None:
            payload["need_address"] = self.need_address

        for value in payload:
            self.base_url+=str(value).replace("_","-") + "=" + str(payload[value])
            self.base_url+="&"

        self.base_url = self.base_url[:-1].replace(" ", "%20")


client = Client(config.yoomoney_token)


async def pay(summa: float):
    name = string.ascii_lowercase + string.digits
    label = config.name + ''.join(random.choice(name) for _ in range(10))
    conn = sqlite3.connect(config.database)
    cur = conn.cursor()
    result = cur.execute("SELECT label FROM unpaid_bills WHERE label = ?", (label,)).fetchone()
    res = await check_buy(label)
    if not res and result is None:
        cur.execute("INSERT INTO unpaid_bills VALUES(?, ?)", (datetime.datetime.now(), label,))
        conn.commit()
        cur.close()
        conn.close()
        quickpay = Quickpay(
            receiver="4100118407708436",
            quickpay_form="shop",
            targets="Пополнение баланса.",
            paymentType="SB",
            sum=summa,
            label=label
        )
        return quickpay.base_url, label
    else:
        conn.close()
        await pay(summa)


async def check_buy(label: str):
    history = await client.operation_history(label=label)
    if history:
        conn = sqlite3.connect(config.database)
        cur = conn.cursor()
        cur.execute("DELETE FROM unpaid_bills WHERE label = ?", (label,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    else:
        return False
