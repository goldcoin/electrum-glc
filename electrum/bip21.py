import re
import urllib
from decimal import Decimal

from . import bitcoin
from .bitcoin import COIN, TOTAL_COIN_SUPPLY_LIMIT_IN_BTC
from .lnaddr import LnDecodeException, lndecode
from .util import format_satoshis_plain

# note: when checking against these, use .lower() to support case-insensitivity
BITCOIN_BIP21_URI_SCHEME = "goldcoin"
LIGHTNING_URI_SCHEME = "lightning"


class InvalidBitcoinURI(Exception):
    pass


def parse_bip21_URI(uri: str) -> dict:
    """Raises InvalidBitcoinURI on malformed URI."""

    if not isinstance(uri, str):
        raise InvalidBitcoinURI(f"expected string, not {uri!r}")

    if ":" not in uri:
        if not bitcoin.is_address(uri):
            raise InvalidBitcoinURI("Not a bitcoin address")
        return {"address": uri}

    u = urllib.parse.urlparse(uri)
    if u.scheme.lower() != BITCOIN_BIP21_URI_SCHEME:
        raise InvalidBitcoinURI("Not a bitcoin URI")
    address = u.path

    # python for android fails to parse query
    if address.find("?") > 0:
        address, query = u.path.split("?")
        pq = urllib.parse.parse_qs(query)
    else:
        pq = urllib.parse.parse_qs(u.query)

    for k, v in pq.items():
        if len(v) != 1:
            raise InvalidBitcoinURI(f"Duplicate Key: {k!r}")

    out = {k: v[0] for k, v in pq.items()}
    if address:
        if not bitcoin.is_address(address):
            raise InvalidBitcoinURI(f"Invalid bitcoin address: {address}")
        out["address"] = address
    if "amount" in out:
        am = out["amount"]
        try:
            m = re.match(r"([0-9.]+)X([0-9])", am)
            if m:
                k = int(m.group(2)) - 8
                amount = Decimal(m.group(1)) * pow(Decimal(10), k)
            else:
                amount = Decimal(am) * COIN
            if amount > TOTAL_COIN_SUPPLY_LIMIT_IN_BTC * COIN:
                raise InvalidBitcoinURI(f"amount is out-of-bounds: {amount!r} BTC")
            out["amount"] = int(amount)
        except Exception as e:
            raise InvalidBitcoinURI(f"failed to parse 'amount' field: {e!r}") from e
    if "message" in out:
        out["message"] = out["message"]
        out["memo"] = out["message"]
    if "time" in out:
        try:
            out["time"] = int(out["time"])
        except Exception as e:
            raise InvalidBitcoinURI(f"failed to parse 'time' field: {e!r}") from e
    if "exp" in out:
        try:
            out["exp"] = int(out["exp"])
        except Exception as e:
            raise InvalidBitcoinURI(f"failed to parse 'exp' field: {e!r}") from e
    if "sig" in out:
        try:
            out["sig"] = bitcoin.base_decode(out["sig"], base=58).hex()
        except Exception as e:
            raise InvalidBitcoinURI(f"failed to parse 'sig' field: {e!r}") from e
    if "lightning" in out:
        try:
            lnaddr = lndecode(out["lightning"])
        except LnDecodeException as e:
            raise InvalidBitcoinURI(f"Failed to decode 'lightning' field: {e!r}") from e
        amount_sat = out.get("amount")
        if amount_sat:
            # allow small leeway due to msat precision
            if abs(amount_sat - int(lnaddr.get_amount_sat())) > 1:
                raise InvalidBitcoinURI("Inconsistent lightning field in bip21: amount")
        address = out.get("address")
        ln_fallback_addr = lnaddr.get_fallback_address()
        if address and ln_fallback_addr:
            if ln_fallback_addr != address:
                raise InvalidBitcoinURI("Inconsistent lightning field in bip21: address")

    return out


def create_bip21_uri(
    addr,
    amount_sat: int | None,
    message: str | None,
    *,
    extra_query_params: dict | None = None,
) -> str:
    if not bitcoin.is_address(addr):
        return ""
    if extra_query_params is None:
        extra_query_params = {}
    query = []
    if amount_sat:
        query.append(f"amount={format_satoshis_plain(amount_sat)}")
    if message:
        query.append(f"message={urllib.parse.quote(message)}")
    for k, v in extra_query_params.items():
        if not isinstance(k, str) or k != urllib.parse.quote(k):
            raise Exception(f"illegal key for URI: {k!r}")
        v = urllib.parse.quote(v)
        query.append(f"{k}={v}")
    p = urllib.parse.ParseResult(
        scheme=BITCOIN_BIP21_URI_SCHEME,
        netloc="",
        path=addr,
        params="",
        query="&".join(query),
        fragment="",
    )
    return str(urllib.parse.urlunparse(p))
