"""Mac helper entry point. Credential bytes stay in the helper process."""

import json
import sys

from ouye_location_studio.auth_helper import (
    CERT_ENV, KEY_ENV, ProviderError, main, read_identity_file, validate_identity,
)
from ouye_location_studio.platforms.macos_identity import APP_SUPPORT, import_identity


def run() -> int:
    if len(sys.argv) == 1:
        main()
        return 0
    try:
        if sys.argv[1:] == ["--import-local"]:
            result = {"identity": import_identity(APP_SUPPORT)}
        elif sys.argv[1:] == ["--validate-local"]:
            validate_identity(read_identity_file(CERT_ENV), read_identity_file(KEY_ENV))
            result = {"valid": True}
        else:
            raise ProviderError("未知认证操作")
    except ProviderError as error:
        result = {"error": str(error)}
    except OSError:
        result = {"error": "无法读写 Mac 本地认证配置，请检查目录权限"}
    print(json.dumps(result, ensure_ascii=False))
    return int("error" in result)


if __name__ == "__main__":
    raise SystemExit(run())
