import boto3
from pydantic import EmailStr

from src.auth.schema import (
    ChangePasswordRequest,
    ConfirmForgotPasswordRequest,
    ConfirmUserRequest,
    UserSignInRequest,
    UserSignUpRequest,
)


class Cognito:
    def __init__(self, region_name: str, user_pool_id: str, user_pool_client_id: str):
        self.client = boto3.client("cognito-idp", region_name=region_name)
        self.user_pool_id = user_pool_id
        self.user_pool_client_id = user_pool_client_id

    def sign_up(self, user: UserSignUpRequest):
        return self.client.sign_up(
            ClientId=self.user_pool_client_id,
            Username=user.email,
            Password=user.password,
        )

    def confirm_sign_up(self, data: ConfirmUserRequest):
        return self.client.confirm_sign_up(
            ClientId=self.user_pool_client_id,
            Username=data.email,
            ConfirmationCode=data.confirmation_code,
        )

    def resend_confirmation_code(self, email: EmailStr):
        return self.client.resend_confirmation_code(
            ClientId=self.user_pool_client_id, Username=email
        )

    def get_user(self, access_token: str):
        return self.client.get_user(AccessToken=access_token)

    def admin_get_user(self, email: EmailStr):
        return self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=email)

    def authenticate_user(self, data: UserSignInRequest):
        return self.client.initiate_auth(
            ClientId=self.user_pool_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": data.email, "PASSWORD": data.password},
        )

    def forgot_password(self, email: EmailStr):
        return self.client.forgot_password(
            ClientId=self.user_pool_client_id, Username=email
        )

    def confirm_forgot_password(self, data: ConfirmForgotPasswordRequest):
        return self.client.confirm_forgot_password(
            ClientId=self.user_pool_client_id,
            Username=data.email,
            ConfirmationCode=data.confirmation_code,
            Password=data.new_password,
        )

    def change_password(self, data: ChangePasswordRequest):
        return self.client.change_password(
            PreviousPassword=data.old_password,
            ProposedPassword=data.new_password,
            AccessToken=data.access_token,
        )

    def authenticate_refresh_token(self, refresh_token: str):
        return self.client.initiate_auth(
            ClientId=self.user_pool_client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
        )

    def sign_out(self, access_token: str):
        return self.client.global_sign_out(AccessToken=access_token)

    def admin_add_user_to_group(self, username: str, group_name: str):
        return self.client.admin_add_user_to_group(
            UserPoolId=self.user_pool_id, Username=username, GroupName=group_name
        )
