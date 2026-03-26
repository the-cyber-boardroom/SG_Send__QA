from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__Capture_Config(Type_Safe):                        # controls what data the API collects and returns per request
    execution_result   : bool = True                            # pass/fail, step timing, error messages
    page_model         : bool = True                            # Schema__*Page snapshot of final page state
    screenshots        : bool = False                           # screenshot at each step (base64 PNG array)
    screenshot_on_fail : bool = True                            # screenshot only on step failure
    video              : bool = False                           # full browser session recording (base64 webm)
    pdf                : bool = False                           # PDF export of final page state (base64)
    browser_console    : bool = False                           # browser console.log/warn/error messages
    browser_trace      : bool = False                           # Playwright trace file (base64 zip)
    python_console     : bool = False                           # Python stdout/stderr captured during execution
    python_trace       : bool = False                           # Python traceback on failure
    performance_data   : bool = True                            # per-step duration, total duration, browser metrics
    prometheus         : bool = True                            # Prometheus exposition format metrics
    network_log        : bool = False                           # all HTTP requests/responses made by browser
