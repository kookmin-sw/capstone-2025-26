import 'package:flutter/material.dart';
import '../../models/signup_step.dart';
import '../../utils/passwordValidator.dart';
import '../../widgets/passwordChecklist.dart';
import '../../widgets/signupInputField.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> with TickerProviderStateMixin {
  final List<TextEditingController> _controllers = [];
  final List<FocusNode> _focusNodes = [];

  final PasswordValidator _passwordValidator = PasswordValidator();
  bool _isPasswordMatch = false;

  late AnimationController _slideController;
  late Animation<Offset> _slideAnimation;
  int _currentStep = 0;

  @override
  void initState() {
    super.initState();
    // 각 단계별 컨트롤러와 포커스 노드 초기화
    for (var i = 0; i < SignupFlow.steps.length; i++) {
      _controllers.add(TextEditingController());
      _focusNodes.add(FocusNode());
    }

    _slideController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOut,
    ));

    _slideController.forward();

    // 첫 번째 필드에 포커스
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _focusNodes[0].requestFocus();
    });

    // 비밀번호 입력 필드 리스너
    _controllers[1].addListener(() {
      if (_controllers[1].text.isNotEmpty) {
        setState(() {
          _passwordValidator.validate(_controllers[1].text);
          if (_controllers[2].text.isNotEmpty) {
            _isPasswordMatch = _passwordValidator.matchPassword(
              _controllers[1].text,
              _controllers[2].text,
            );
          }
        });
      }
    });

    // 비밀번호 확인 필드 리스너
    _controllers[2].addListener(() {
      if (_controllers[2].text.isNotEmpty) {
        setState(() {
          _isPasswordMatch = _passwordValidator.matchPassword(
            _controllers[1].text,
            _controllers[2].text,
          );
        });
      }
    });
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    for (var focusNode in _focusNodes) {
      focusNode.dispose();
    }
    _slideController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < SignupFlow.steps.length - 1) {
      setState(() {
        _currentStep++;
        _slideController.reset();
        _slideController.forward();
        // 다음 필드로 포커스 이동
        _focusNodes[_currentStep].requestFocus();
      });
    }
  }

  bool _canMoveToNextStep(int step) {
    if (step == 1) {
      return _passwordValidator.isValid;
    }
    return _controllers[step].text.isNotEmpty;
  }

  Widget _buildCurrentStep() {
    return SlideTransition(
      position: _slideAnimation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            SignupFlow.steps[_currentStep].title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          if (SignupFlow.steps[_currentStep].subtitle != null)
            Text(
              SignupFlow.steps[_currentStep].subtitle!,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
          const SizedBox(height: 16),
          _buildInputField(_currentStep),
          if (_currentStep == 1 && _controllers[1].text.isNotEmpty)
            PasswordChecklist(validator: _passwordValidator),
          if (_currentStep == 2 && _controllers[2].text.isNotEmpty)
            _buildPasswordMatchIndicator(),
        ],
      ),
    );
  }

  Widget _buildInputField(int step) {
    final stepConfig = SignupFlow.steps[step];
    return SignupInputField(
      controller: _controllers[step],
      focusNode: _focusNodes[step],
      hintText: stepConfig.hintText,
      isPassword: stepConfig.isPassword,
      onChanged: (value) {
        setState(() {
          if (step == 1) {
            _passwordValidator.validate(_controllers[1].text);
          } else if (step == 2) {}
        });
      },
      onSubmitted: (_) {
        if (_canMoveToNextStep(step)) {
          print(
              'Step ${step + 1} (${stepConfig.shortTitle}): ${_controllers[step].text}');

          //제출 시 value값 출력하는 디버그 로그 추가

          if (step < SignupFlow.steps.length - 1) {
            _nextStep();
          } else if (step == 2 && _isPasswordMatch) {
            // TODO: 회원가입 완료 처리
            print('회원가입 정보:');
            print('닉네임: ${_controllers[0].text}');
            print('비밀번호: ${_controllers[1].text}');
            print('비밀번호 확인: ${_controllers[2].text}');
          }
        }
      },
      onTapOutside: (_) {
        if (_canMoveToNextStep(step)) {
          _nextStep();
        }
      },
    );
  }

  Widget _buildPasswordMatchIndicator() {
    return Padding(
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
    );
  }

  Widget _buildPreviousStep(int index) {
    final step = SignupFlow.steps[index];
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            step.shortTitle,
            style: const TextStyle(
              color: Colors.grey,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          _buildInputField(index),
          if (index == 1 && _controllers[1].text.isNotEmpty)
            PasswordChecklist(validator: _passwordValidator),
          if (index == 2 && _controllers[2].text.isNotEmpty)
            _buildPasswordMatchIndicator(),
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
          icon: const Icon(Icons.arrow_back_ios),
          color: Colors.white,
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildCurrentStep(),
              if (_currentStep > 0) ...[
                const SizedBox(height: 40),
                ...List.generate(
                  _currentStep,
                  (index) => _buildPreviousStep(index),
                ).reversed,
              ],
            ],
          ),
        ),
      ),
    );
  }
}
