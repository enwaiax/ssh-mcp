# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "76f6ac18-6106-43b9-9890-f6fa34c57067"
#   Timestamp: "2025-08-05T17:01:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则)"
#   Quality_Check: "Pydantic模型完整实现，包含验证器和类型注解，与TypeScript版本功能对等"
# }}
# {{START_MODIFICATIONS}}
"""
Data Models Module

This module contains Pydantic data models for SSH configurations,
MCP tool parameters, responses, and other data structures.
Provides runtime validation and type safety equivalent to TypeScript interfaces.
"""

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError


class LogLevel(str, Enum):
    """Log levels enum equivalent to TypeScript LogLevel type"""

    INFO = "info"
    ERROR = "error"
    DEBUG = "debug"


class SSHConfig(BaseModel):
    """
    SSH connection configuration model.
    Equivalent to TypeScript SSHConfig interface.
    """

    name: str | None = Field(
        default=None, description="Connection name, optional for compatibility"
    )
    host: str = Field(..., description="SSH server hostname or IP address")
    port: int = Field(default=22, description="SSH server port")
    username: str = Field(..., description="SSH username")
    password: str | None = Field(default=None, description="SSH password")
    private_key: str | None = Field(
        default=None, alias="privateKey", description="Path to SSH private key file"
    )
    passphrase: str | None = Field(default=None, description="Private key passphrase")
    command_whitelist: list[str] | None = Field(
        default=None,
        alias="commandWhitelist",
        description="Command whitelist (array of regex patterns)",
    )
    command_blacklist: list[str] | None = Field(
        default=None,
        alias="commandBlacklist",
        description="Command blacklist (array of regex patterns)",
    )

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number is in valid range"""
        if not 1 <= v <= 65535:
            raise PydanticCustomError(
                "invalid_port",
                "Port must be between 1 and 65535, got {port}",
                {"port": v},
            )
        return v

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate host is not empty"""
        if not v.strip():
            raise PydanticCustomError("empty_host", "Host cannot be empty", {})
        return v.strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username is not empty"""
        if not v.strip():
            raise PydanticCustomError("empty_username", "Username cannot be empty", {})
        return v.strip()

    @field_validator("private_key")
    @classmethod
    def validate_private_key_path(cls, v: str | None) -> str | None:
        """Validate private key file exists if provided"""
        if v is not None:
            # Expand user path (~)
            expanded_path = Path(v).expanduser()
            if not expanded_path.exists():
                raise PydanticCustomError(
                    "private_key_not_found",
                    "Private key file not found: {path}",
                    {"path": str(expanded_path)},
                )
            if not expanded_path.is_file():
                raise PydanticCustomError(
                    "private_key_not_file",
                    "Private key path is not a file: {path}",
                    {"path": str(expanded_path)},
                )
            return str(expanded_path)
        return v

    @model_validator(mode="after")
    def validate_auth_method(self) -> "SSHConfig":
        """Ensure at least one authentication method is provided"""
        if not self.password and not self.private_key:
            raise PydanticCustomError(
                "no_auth_method",
                "Either password or private_key must be provided for authentication",
                {},
            )
        return self

    class Config:
        """Pydantic configuration"""

        populate_by_name = True  # Allow both snake_case and camelCase field names
        str_strip_whitespace = True
        validate_assignment = True


# Type alias equivalent to TypeScript SshConnectionConfigMap
SshConnectionConfigMap = dict[str, SSHConfig]


class ExecuteCommandParams(BaseModel):
    """Parameters for execute-command MCP tool"""

    cmd_string: str = Field(..., alias="cmdString", description="Command to execute")
    connection_name: str | None = Field(
        default=None,
        alias="connectionName",
        description="SSH connection name (optional, default is 'default')",
    )

    @field_validator("cmd_string")
    @classmethod
    def validate_cmd_string(cls, v: str) -> str:
        """Validate command string is not empty"""
        if not v.strip():
            raise PydanticCustomError(
                "empty_command", "Command string cannot be empty", {}
            )
        return v.strip()

    class Config:
        populate_by_name = True


class UploadParams(BaseModel):
    """Parameters for upload MCP tool"""

    local_path: str = Field(..., alias="localPath", description="Local file path")
    remote_path: str = Field(..., alias="remotePath", description="Remote file path")
    connection_name: str | None = Field(
        default=None,
        alias="connectionName",
        description="SSH connection name (optional, default is 'default')",
    )

    @field_validator("local_path")
    @classmethod
    def validate_local_path(cls, v: str) -> str:
        """Validate local file exists"""
        path = Path(v).expanduser()
        if not path.exists():
            raise PydanticCustomError(
                "local_file_not_found",
                "Local file not found: {path}",
                {"path": str(path)},
            )
        if not path.is_file():
            raise PydanticCustomError(
                "local_path_not_file",
                "Local path is not a file: {path}",
                {"path": str(path)},
            )
        return str(path)

    @field_validator("remote_path")
    @classmethod
    def validate_remote_path(cls, v: str) -> str:
        """Validate remote path is not empty"""
        if not v.strip():
            raise PydanticCustomError(
                "empty_remote_path", "Remote path cannot be empty", {}
            )
        return v.strip()

    class Config:
        populate_by_name = True


class DownloadParams(BaseModel):
    """Parameters for download MCP tool"""

    remote_path: str = Field(..., alias="remotePath", description="Remote file path")
    local_path: str = Field(..., alias="localPath", description="Local file path")
    connection_name: str | None = Field(
        default=None,
        alias="connectionName",
        description="SSH connection name (optional, default is 'default')",
    )

    @field_validator("remote_path")
    @classmethod
    def validate_remote_path(cls, v: str) -> str:
        """Validate remote path is not empty"""
        if not v.strip():
            raise PydanticCustomError(
                "empty_remote_path", "Remote path cannot be empty", {}
            )
        return v.strip()

    @field_validator("local_path")
    @classmethod
    def validate_local_path(cls, v: str) -> str:
        """Validate local path and ensure directory exists"""
        path = Path(v).expanduser()
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)

    class Config:
        populate_by_name = True


class ListServersParams(BaseModel):
    """Parameters for list-servers MCP tool (no parameters required)"""

    pass


class MCPContent(BaseModel):
    """MCP content format"""

    type: Literal["text"] = Field(default="text", description="Content type")
    text: str = Field(..., description="Content text")


class MCPResponse(BaseModel):
    """MCP response format"""

    content: list[MCPContent] = Field(..., description="Response content")
    is_error: bool | None = Field(
        default=None, alias="isError", description="Error flag"
    )

    class Config:
        populate_by_name = True


class ServerInfo(BaseModel):
    """Server information model for list-servers response"""

    name: str = Field(..., description="Connection name")
    host: str = Field(..., description="Server hostname")
    port: int = Field(..., description="Server port")
    username: str = Field(..., description="Username")
    connected: bool = Field(..., description="Connection status")


# Export all models
__all__ = [
    "LogLevel",
    "SSHConfig",
    "SshConnectionConfigMap",
    "ExecuteCommandParams",
    "UploadParams",
    "DownloadParams",
    "ListServersParams",
    "MCPContent",
    "MCPResponse",
    "ServerInfo",
]
# {{END_MODIFICATIONS}}
