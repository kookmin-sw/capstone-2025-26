import 'package:flutter/material.dart';
import 'package:reme/themes/color.dart';

class ChallengeTypeItem extends StatelessWidget {
  final String title;
  final String description;
  final int score;
  final bool hasSuccess;
  final String imagePath;

  const ChallengeTypeItem({
    required this.title,
    required this.description,
    required this.score,
    required this.hasSuccess,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(21.0, 0.0, 21.0, 0),
      padding: const EdgeInsets.all(16.0),
      decoration: const BoxDecoration(
        color: background,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: const Color(0xFF333333),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Image.asset(
                  imagePath,
                  width: 32,
                  height: 32,
                  errorBuilder: (context, error, stackTrace) => const Icon(
                    Icons.image_not_supported,
                    color: Colors.grey,
                    size: 24,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontFamily: 'Pretendard',
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            description,
            style: const TextStyle(
              color: Colors.white,
              fontFamily: 'Pretendard',
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                hasSuccess ? Icons.local_fire_department : Icons.warning,
                color: hasSuccess ? Colors.orange : Colors.yellow,
                size: 24,
              ),
              const SizedBox(width: 4),
              Text(
                "$score/100",
                style: TextStyle(
                  color: hasSuccess ? Colors.orange : Colors.yellow,
                  fontFamily: 'Pretendard',
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
