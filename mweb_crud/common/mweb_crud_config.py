class MWebCRUDConfig:
    # API Config
    PAGE_PARAM_NAME: str = "page"
    ITEM_PER_PAGE_PARAM_NAME: str = "per-page"
    SEARCH_FIELD_PARAM_NAME: str = "search"
    TOTAL_ITEM_PER_PAGE: int = 25
    SORT_FIELD_PARAM_NAME: str = "sort-field"
    SORT_ORDER_PARAM_NAME: str = "sort-order"
    SORT_DEFAULT_ORDER_NAME: str = "desc"
    SORT_DEFAULT_FIELD_NAME: str = "id"

    # Swagger UI Config
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_SWAGGER_AUTH: bool = False
    SWAGGER_AUTH_USERNAME: str = "mweb"
    SWAGGER_AUTH_PASSWORD: str = "mweb12"
    SWAGGER_JSON_URL: str = "/swagger-json"
    SWAGGER_UI_URL: str = "/swagger-ui"
    SWAGGER_UI_ASSETS_URL: str = "/swagger-assets"
    SWAGGER_DEFAULT_TAG_NAME: str = "Common"
    SWAGGER_TITLE: str = "MWeb Swagger"
    SWAGGER_APP_VERSION: str = "1.0.0"

    ENABLED_JWT_AUTH: bool = True

    # Messages
    UNKNOWN_ERROR: str = "Unknown Error Occurred!"

    # File Upload
    FILE_SIZE_NOT_MATCH: str = "File size is bigger than allowed"
    INVALID_FILE_EXTENSION: str = "Invalid uploaded file"
    INVALID_FILE_UPLOAD_PATH: str = "Invalid upload path"

    # Display Messages
    CREATE_SUCCESS_MSG: str = "Created successfully."
    DELETE_SUCCESS_MSG = "Deleted successfully."
    FAILED_TO_DELETE_RECORD_MSG = "Failed to delete record."
    UPDATE_SUCCESS_MSG = "Updated successfully."
    INVALID_INPUT_DATA_MSG = "Invalid input data."
    FAILED_TO_SAVE_DATA_MSG = "Failed to save data."
    FAILED_TO_UPDATE_DATA_MSG = "Failed to update data."

    INVALID_JSON_REQUEST_DATA_MSG = "Invalid JSON request data."
    DATA_VALIDATION_ERROR_MSG = "Data validation error!"
    RECORD_NOT_FOUND_MSG = "Record not found."

