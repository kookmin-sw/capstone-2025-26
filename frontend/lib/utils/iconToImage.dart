import 'dart:ui' as ui;
import 'dart:typed_data';
import 'package:flutter/material.dart';

Future<ImageProvider> IconToImage(Icon icon, {double size = 48.0}) async {
  final ui.PictureRecorder recorder = ui.PictureRecorder();
  final Canvas canvas = Canvas(recorder);

  final TextPainter textPainter = TextPainter(
    textDirection: TextDirection.ltr,
    text: TextSpan(
      text: String.fromCharCode(icon.icon!.codePoint),
      style: TextStyle(
        fontSize: size,
        fontFamily: icon.icon!.fontFamily,
        package: icon.icon!.fontPackage,
        color: icon.color,
      ),
    ),
  );

  textPainter.layout();
  textPainter.paint(canvas, Offset.zero);
  print(canvas);

  final ui.Image image = await recorder.endRecording().toImage(size.toInt(), size.toInt());
  final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
  if (byteData == null) {
    throw Exception("Failed to convert Icon to Image");
  }

  return MemoryImage(byteData.buffer.asUint8List());
}
