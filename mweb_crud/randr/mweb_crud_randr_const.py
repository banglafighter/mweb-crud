class MWebRESTResponseStatus:
    success = "success"
    error = "error"


class MWebRESTResponseCode:
    # SUCCESS Codes
    success = 2200

    # ERROR Codes
    error = 5100
    validation_error = 5101

    invalid_token_code = 5500
    token_expired_code = 5501
    token_error_code = 5502

    unauthorized = 4100
