import 'package:flutter/material.dart';
import '../utils/passwordValidator.dart';

class PasswordChecklist extends StatelessWidget {
  final PasswordValidator validator;

  const PasswordChecklist({
    super.key,
    required this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 16, left: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCheckItem('8자 이상', validator.isLengthValid),
          _buildCheckItem('영문 포함', validator.hasLetters),
          _buildCheckItem('숫자 포함', validator.hasNumbers),
          _buildCheckItem('특수문자 포함 (@\$!%*#?&)', validator.hasSpecialChars),
        ],
      ),
    );
  }

  Widget _buildCheckItem(String text, bool isValid) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(
            isValid ? Icons.check_circle : Icons.check_circle_outline,
            size: 16,
            color: isValid ? Colors.green[400] : Colors.grey,
          ),
          const SizedBox(width: 8),
          Text(
            text,
            style: TextStyle(
              color: isValid ? Colors.green[400] : Colors.grey,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
