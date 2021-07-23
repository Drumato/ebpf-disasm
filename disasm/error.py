import dataclasses
from enum import Enum, auto


class ErrorReason(Enum):
    CANNOT_FOUND_EBPF_FUNCTION = auto()


@dataclasses.dataclass
class Error:
    reason: ErrorReason
    message: str

    def reason_to_str(self) -> str:
        if self.reason == ErrorReason.CANNOT_FOUND_EBPF_FUNCTION:
            return "Cannot found any eBPF functions on a ELF"
        else:
            return ""

    def fatal_message(self) -> str:
        return f"{self.reason_to_str()} ERROR: {self.message}"
