import 'package:flutter/material.dart';

class SignupStep {
  final String title;
  final String? subtitle;
  final String hintText;
  final String shortTitle;
  final bool isPassword;
  final bool requiresValidation;
  final String? Function(String?)? validator;

  const SignupStep({
    required this.title,
    this.subtitle,
    required this.hintText,
    required this.shortTitle,
    this.isPassword = false,
    this.requiresValidation = false,
    this.validator,
  });
}

class SignupFlow {
  static const List<SignupStep> steps = [
    SignupStep(
      title: "To-Go에서 사용할\n닉네임을 알려주세요!",
      subtitle: "앱에서 크루별 닉네임을 설정할 수 있어요!",
      hintText: "닉네임",
      shortTitle: "닉네임",
    ),
    SignupStep(
      title: "회원정보 수정에 사용할\n비밀번호를 입력해주세요",
      subtitle: "영문, 숫자, 특수문자(@\$!%*#?&) 포함 8자 이상",
      hintText: "비밀번호",
      shortTitle: "비밀번호",
      isPassword: true,
      requiresValidation: true,
    ),
    SignupStep(
      title: "비밀번호를\n한번 더 입력해주세요",
      subtitle: "비밀번호 확인을 위해 한번 더 입력해주세요",
      hintText: "비밀번호 확인",
      shortTitle: "비밀번호 확인",
      isPassword: true,
      requiresValidation: true,
    ),
  ];
}
