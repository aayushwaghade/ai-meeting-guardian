import pywhatkit

phone = "+919404319706"

message = "🔥 AI Meeting Guardian Activated"

pywhatkit.sendwhatmsg_instantly(
    phone_no=phone,
    message=message,
    wait_time=30,
    tab_close=False,
    close_time=3
)