class UserInfo {
  String? accessToken;
  String? refreshToken;
  String? userName;
  String? email;
  String? id;
  String? profileImage;
  bool? needSignup;
  UserInfo(this.accessToken, this.refreshToken, this.userName, this.email,
      this.id, this.profileImage, this.needSignup);
}
