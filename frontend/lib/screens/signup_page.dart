import 'package:flutter/material.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> with TickerProviderStateMixin {
  final TextEditingController _nicknameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();

  final FocusNode _nicknameFocus = FocusNode();
  final FocusNode _passwordFocus = FocusNode();
  final FocusNode _confirmPasswordFocus = FocusNode();

  int _currentStep = 0;
  late final AnimationController _slideController;
  late final Animation<Offset> _slideAnimation;

  final List<String> _titles = [
    "Re:ME에서 사용할\n닉네임을 알려주세요!",
    "Re:ME에서 사용할\n비밀번호를 입력해주세요",
    "비밀번호를\n한번 더 입력해주세요",
  ];

  bool _isPasswordValid = false;
  bool _isPasswordMatch = false;

  // 비밀번호 각 조건별 상태
  bool _isLengthValid = false;
  bool _hasLetters = false;
  bool _hasNumbers = false;
  bool _hasSpecialChars = false;

  bool _validatePassword(String password) {
    _isLengthValid = password.length >= 8;
    _hasLetters = RegExp(r'[A-Za-z]').hasMatch(password);
    _hasNumbers = RegExp(r'\d').hasMatch(password);
    _hasSpecialChars = RegExp(r'[@$!%*#?&]').hasMatch(password);

    setState(() {
      _isPasswordValid =
          _isLengthValid && _hasLetters && _hasNumbers && _hasSpecialChars;
    });
    return _isPasswordValid;
  }

  void _checkPasswordMatch(String confirmPassword) {
    setState(() {
      _isPasswordMatch = confirmPassword == _passwordController.text;
    });
  }

  @override
  void initState() {
    super.initState();
    _slideController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -0.1),
      end: const Offset(0, 0),
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOut,
    ));
    _slideController.forward();

    // 첫 화면에서 자동으로 닉네임 입력 필드에 포커스
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _nicknameFocus.requestFocus();
    });

    _passwordController.addListener(() {
      _validatePassword(_passwordController.text);
      if (_confirmPasswordController.text.isNotEmpty) {
        _checkPasswordMatch(_confirmPasswordController.text);
      }
    });

    _confirmPasswordController.addListener(() {
      _checkPasswordMatch(_confirmPasswordController.text);
    });
  }

  @override
  void dispose() {
    _nicknameController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _nicknameFocus.dispose();
    _passwordFocus.dispose();
    _confirmPasswordFocus.dispose();
    _slideController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < _titles.length - 1) {
      _slideController.reverse().then((_) {
        setState(() {
          _currentStep++;
        });
        _slideController.forward();

        // 다음 스텝의 입력 필드에 자동 포커스
        WidgetsBinding.instance.addPostFrameCallback((_) {
          switch (_currentStep) {
            case 1:
              _passwordFocus.requestFocus();
              break;
            case 2:
              _confirmPasswordFocus.requestFocus();
              break;
          }
        });
      });
    }
  }

  void _goToStep(int step) {
    _slideController.reverse().then((_) {
      setState(() {
        _currentStep = step;
      });
      _slideController.forward();
    });
  }

  Widget _buildCurrentStep() {
    return SlideTransition(
      position: _slideAnimation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            _titles[_currentStep],
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          if (_currentStep == 0)
            const Text(
              '(앱에서 크루별 닉네임을 설정할 수 있어요!)',
              style: TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
          const SizedBox(height: 16),
          Container(
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: BorderRadius.circular(8),
            ),
            child: _buildTextField(_currentStep),
          ),
          if (_currentStep == 1 && _passwordController.text.isNotEmpty)
            _buildPasswordChecklist(),
          if (_currentStep == 2 && _confirmPasswordController.text.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 16, left: 8),
              child: Row(
                children: [
                  Icon(
                    _isPasswordMatch ? Icons.check_circle : Icons.error,
                    size: 16,
                    color: _isPasswordMatch ? Colors.green[400] : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _isPasswordMatch ? '비밀번호가 일치합니다' : '비밀번호가 일치하지 않습니다',
                    style: TextStyle(
                      color: _isPasswordMatch ? Colors.green[400] : Colors.red,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildPasswordChecklist() {
    return Padding(
      padding: const EdgeInsets.only(top: 16, left: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildChecklistItem(_isLengthValid, '8자 이상'),
          _buildChecklistItem(_hasLetters, '영문 포함'),
          _buildChecklistItem(_hasNumbers, '숫자 포함'),
          _buildChecklistItem(_hasSpecialChars, '특수문자 포함 (@\$!%*#?&)'),
        ],
      ),
    );
  }

  Widget _buildChecklistItem(bool isValid, String text) {
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

  Widget _buildTextField(int step) {
    switch (step) {
      case 0:
        return TextField(
          controller: _nicknameController,
          focusNode: _nicknameFocus,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            hintText: "닉네임",
            hintStyle: TextStyle(color: Colors.grey),
            contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            border: InputBorder.none,
            enabledBorder: InputBorder.none,
            focusedBorder: InputBorder.none,
          ),
          onSubmitted: (_) => _nextStep(),
          onTapOutside: (_) {
            if (_nicknameController.text.isNotEmpty) {
              _nextStep();
            }
          },
        );
      case 1:
        return TextField(
          controller: _passwordController,
          focusNode: _passwordFocus,
          style: const TextStyle(color: Colors.white),
          obscureText: true,
          decoration: const InputDecoration(
            hintText: "비밀번호",
            hintStyle: TextStyle(color: Colors.grey),
            contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            border: InputBorder.none,
            enabledBorder: InputBorder.none,
            focusedBorder: InputBorder.none,
          ),
          onChanged: (value) {
            setState(() {
              _validatePassword(value);
              if (_confirmPasswordController.text.isNotEmpty) {
                _checkPasswordMatch(_confirmPasswordController.text);
              }
            });
          },
          onSubmitted: (_) {
            if (_isPasswordValid) _nextStep();
          },
          onTapOutside: (_) {
            if (_passwordController.text.isNotEmpty && _isPasswordValid) {
              _nextStep();
            }
          },
        );
      case 2:
        return TextField(
          controller: _confirmPasswordController,
          focusNode: _confirmPasswordFocus,
          style: const TextStyle(color: Colors.white),
          obscureText: true,
          decoration: const InputDecoration(
            hintText: "비밀번호 확인",
            hintStyle: TextStyle(color: Colors.grey),
            contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            border: InputBorder.none,
            enabledBorder: InputBorder.none,
            focusedBorder: InputBorder.none,
          ),
          onSubmitted: (_) {
            if (_isPasswordMatch) {
              // 회원가입 완료 처리
            }
          },
        );
      default:
        return const SizedBox();
    }
  }

  Widget _buildPreviousStep(int index) {
    FocusNode getFocusNode(int index) {
      switch (index) {
        case 0:
          return _nicknameFocus;
        case 1:
          return _passwordFocus;
        case 2:
          return _confirmPasswordFocus;
        default:
          return _nicknameFocus;
      }
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            _titles[index].split('\n')[1],
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: BorderRadius.circular(8),
            ),
            child: TextField(
              controller: index == 0
                  ? _nicknameController
                  : index == 1
                      ? _passwordController
                      : _confirmPasswordController,
              focusNode: getFocusNode(index),
              style: const TextStyle(color: Colors.white),
              obscureText: index > 0,
              decoration: InputDecoration(
                hintText: index == 0
                    ? "닉네임"
                    : index == 1
                        ? "비밀번호"
                        : "비밀번호 확인",
                hintStyle: const TextStyle(color: Colors.grey),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                border: InputBorder.none,
                enabledBorder: InputBorder.none,
                focusedBorder: InputBorder.none,
              ),
              onChanged: (value) {
                if (index == 1) {
                  _validatePassword(value);
                  if (_confirmPasswordController.text.isNotEmpty) {
                    _checkPasswordMatch(_confirmPasswordController.text);
                  }
                } else if (index == 2) {
                  _checkPasswordMatch(value);
                }
              },
              onSubmitted: (_) {
                if (index < _currentStep - 1) {
                  FocusScope.of(context).nextFocus();
                }
              },
            ),
          ),
          if (index == 1 && _passwordController.text.isNotEmpty)
            _buildPasswordChecklist(),
          if (index == 2 && _confirmPasswordController.text.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 16, left: 8),
              child: Row(
                children: [
                  Icon(
                    _isPasswordMatch ? Icons.check_circle : Icons.error,
                    size: 16,
                    color: _isPasswordMatch ? Colors.green[400] : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _isPasswordMatch ? '비밀번호가 일치합니다' : '비밀번호가 일치하지 않습니다',
                    style: TextStyle(
                      color: _isPasswordMatch ? Colors.green[400] : Colors.red,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const ClampingScrollPhysics(),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildCurrentStep(),
                if (_currentStep > 0) ...[
                  const SizedBox(height: 40),
                  ...List.generate(_currentStep,
                      (index) => _buildPreviousStep(_currentStep - 1 - index)),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
