class PasswordValidator {
  bool isLengthValid = false;
  bool hasLetters = false;
  bool hasNumbers = false;
  bool hasSpecialChars = false;
  bool isValid = false;

  void validate(String password) {
    isLengthValid = password.length >= 8;
    hasLetters = RegExp(r'[A-Za-z]').hasMatch(password);
    hasNumbers = RegExp(r'\d').hasMatch(password);
    hasSpecialChars = RegExp(r'[@$!%*#?&]').hasMatch(password);
    isValid = isLengthValid && hasLetters && hasNumbers && hasSpecialChars;
  }

  bool matchPassword(String password, String confirmPassword) {
    return password == confirmPassword;
  }
}
