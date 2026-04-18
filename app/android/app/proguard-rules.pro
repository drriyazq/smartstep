# SmartStep ProGuard rules.
# R8 minify + shrinkResources are enabled for release — keep rules listed
# here whenever a library uses reflection or native bindings.

# ── Flutter engine ───────────────────────────────────────────────
-keep class io.flutter.embedding.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.plugins.** { *; }
-dontwarn io.flutter.embedding.**

# ── Firebase (Auth, Messaging, Crashlytics, Analytics) ───────────
-keep class com.google.firebase.** { *; }
-dontwarn com.google.firebase.**
# Crashlytics keeps unobfuscated stack frames — required for readable crashes
-keepattributes SourceFile,LineNumberTable
-keep public class * extends java.lang.Exception

# ── Hive (uses reflection for TypeAdapters) ──────────────────────
-keep class * extends io.hive.TypeAdapter
-keepclassmembers class * {
    @hive.HiveField <fields>;
}

# ── flutter_secure_storage ───────────────────────────────────────
-keep class com.it_nomads.fluttersecurestorage.** { *; }

# ── Share Plus — uses FileProvider reflection ────────────────────
-keep class dev.fluttercommunity.plus.share.** { *; }

# ── Dio / OkHttp — HTTP stack ────────────────────────────────────
-keep class okio.** { *; }
-dontwarn okio.**
-keep class com.squareup.okhttp3.** { *; }
-dontwarn com.squareup.okhttp3.**

# ── go_router / Riverpod (code-gen friendly; keep enclosing classes) ─
-keep class **$Companion { *; }
