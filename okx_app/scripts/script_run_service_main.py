from okx_app.services.service_main import ServiceMain

def run():
    ServiceMain().get_markets(historicals=False)