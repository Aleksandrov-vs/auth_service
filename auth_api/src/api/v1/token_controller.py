from flask import Blueprint, jsonify, request, json
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, ValidationError

from src.api.v1.utils import body_fields_validate_with_pydantic
from src.services.token_service import get_token_service
from src.repositories import token_rep


token = Blueprint('token', __name__, url_prefix='/api/v1/auth')


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@token.route('/change-password', methods=["POST"])
@jwt_required()
@body_fields_validate_with_pydantic(ChangePasswordRequest)
def change_password():
    token_service = get_token_service(token_rep.get_token_repository())
    token_inf = json.loads(get_jwt_identity())
    body = ChangePasswordRequest(**json.loads(request.data))

    http_status, response_msg = token_service.change_password(
        token_inf,
        body.old_password,
        body.new_password
    )
    return jsonify(response_msg), http_status


class LoginRequest(BaseModel):
    login: str
    password: str


@token.route('/login',  methods=["POST"])
@body_fields_validate_with_pydantic(LoginRequest)
def login():
    token_service = get_token_service(token_rep.get_token_repository())
    body = LoginRequest(**json.loads(request.data))

    http_status, response_msg = token_service.login(body.login, body.password, request.user_agent)
    return jsonify(response_msg), http_status


class LogoutRequest(BaseModel):
    refresh_token: str


@token.route('/logout')
@body_fields_validate_with_pydantic(LogoutRequest)
def logout():
    token_service = get_token_service(token_rep.get_token_repository())
    body = LogoutRequest(**json.loads(request.data))

    http_status, response_msg = token_service.logout(body.refresh_token)
    return jsonify(response_msg), http_status


class ReworkTokensRequest(BaseModel):
    refresh_token: str


@token.route('/refresh-tokens', methods=["POST"])
@body_fields_validate_with_pydantic(ReworkTokensRequest)
def refresh_tokens():
    token_service = get_token_service(token_rep.get_token_repository())
    body = ReworkTokensRequest(**json.loads(request.data))
    http_status, response_msg = token_service.refresh_tokens(body.refresh_token)
    return jsonify(response_msg), http_status


class RegisterRequest(BaseModel):
    login: str
    password: str


@token.route('/register', methods=["POST"])
@body_fields_validate_with_pydantic(RegisterRequest)
def register():
    token_service = get_token_service(token_rep.get_token_repository())
    body = RegisterRequest(**json.loads(request.data))

    http_status, response_msg = token_service.register(body.login, body.password, request.user_agent)
    return jsonify(response_msg), http_status
