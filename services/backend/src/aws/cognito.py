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
        """
        Registers a new user in the Cognito user pool.

        Args:
            user (UserSignUpRequest): User sign-up request data.
        """
        return self.client.sign_up(
            ClientId=self.user_pool_client_id,
            Username=user.email,
            Password=user.password,
        )

    def verify_email(self, data: ConfirmUserRequest):
        """
        Confirms a user's email address with a confirmation code.

        Args:
            data (ConfirmUserRequest): Confirmation request data.
        """
        return self.client.confirm_sign_up(
            ClientId=self.user_pool_client_id,
            Username=data.email,
            ConfirmationCode=data.confirmation_code,
        )

    def resend_confirmation_code(self, email: EmailStr):
        """
        Resends the confirmation code to the user's email.

        Args:
            email (EmailStr): User's email address.
        """
        return self.client.resend_confirmation_code(
            ClientId=self.user_pool_client_id, Username=email
        )

    def get_user(self, access_token: str):
        """
        Retrieves user information using an access token.

        Args:
            access_token (str): Access token.
        """
        return self.client.get_user(AccessToken=access_token)

    def admin_get_user(self, email: EmailStr):
        """
        Retrieves user information as an admin using the user's email.

        Args:
            email (EmailStr): User's email address.
        """
        return self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=email)

    def authenticate_user(self, data: UserSignInRequest):
        """
        Authenticates a user with their email and password.

        Args:
            data (UserSignInRequest): User sign-in request data.
        """
        return self.client.initiate_auth(
            ClientId=self.user_pool_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": data.email, "PASSWORD": data.password},
        )

    def forgot_password(self, email: EmailStr):
        """
        Initiates the forgot password flow for a user.

        Args:
            email (EmailStr): User's email address.
        """
        return self.client.forgot_password(
            ClientId=self.user_pool_client_id, Username=email
        )

    def confirm_forgot_password(self, data: ConfirmForgotPasswordRequest):
        """
        Confirms a new password for a user who has forgotten their password.

        Args:
            data (ConfirmForgotPasswordRequest): Confirmation request data.
        """
        return self.client.confirm_forgot_password(
            ClientId=self.user_pool_client_id,
            Username=data.email,
            ConfirmationCode=data.confirmation_code,
            Password=data.new_password,
        )

    def change_password(self, data: ChangePasswordRequest):
        """
        Changes the password for an authenticated user.

        Args:
            data (ChangePasswordRequest): Change password request data.
        """
        return self.client.change_password(
            PreviousPassword=data.old_password,
            ProposedPassword=data.new_password,
            AccessToken=data.access_token,
        )

    def authenticate_refresh_token(self, refresh_token: str):
        """
        Authenticates a user using a refresh token.

        Args:
            refresh_token (str): Refresh token.
        """
        return self.client.initiate_auth(
            ClientId=self.user_pool_client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token},
        )

    def sign_out(self, access_token: str):
        """
        Signs out a user globally using their access token.

        Args:
            access_token (str): Access token.
        """
        return self.client.global_sign_out(AccessToken=access_token)

    def admin_add_user_to_group(self, username: str, group_name: str):
        """
        Adds a user to an existing Cognito group with admin privileges.

        Args:
            username (str): Cognito username (email).
            group_name (str): Name of the Cognito group.
        """
        return self.client.admin_add_user_to_group(
            UserPoolId=self.user_pool_id, Username=username, GroupName=group_name
        )
