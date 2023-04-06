    ######################################
    # Decorator imports Rest Api Headers #
    ######################################


def decorator_rest_headers_required(function=None):
    """
    Decorator for Exchange Rest Api use.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs["headers"] = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36" 
                }
            return func(*args, **kwargs)
        return wrapper

    if function:
        return decorator(function)

    return decorator