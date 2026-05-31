#!/usr/bin/env python3
"""Generate a valid Xcode project.pbxproj for SelePic iOS app."""
import os

# Unique UUIDs - using real-ish UUIDs
UUIDS = {
    'root': 'A1B2C3D4E5F6000100020003',
    'target': 'A1B2C3D4E5F6000100040005',
    'bundle_id': 'A1B2C3D4E5F6000100060007',

    # Sources build phase
    'sources_phase': 'A1B2C3D4E5F6000100080009',
    'resources_phase': 'A1B2C3D4E5F60001000A000B',
    'frameworks_phase': 'A1B2C3D4E5F60001000C000D',
    'product_ref': 'A1B2C3D4E5F60001000E000F',

    # PBXBuildFile refs (build file UUIDs)
    'bf_app': 'A1B2C3D4E5F6001000010001',
    'bf_content': 'A1B2C3D4E5F6001000010002',
    'bf_album': 'A1B2C3D4E5F6001000010003',
    'bf_data': 'A1B2C3D4E5F6001000010004',
    'bf_photoitem': 'A1B2C3D4E5F6001000010005',
    'bf_imageloader': 'A1B2C3D4E5F6001000010006',
    'bf_picker': 'A1B2C3D4E5F6001000010007',
    'bf_sharesheet': 'A1B2C3D4E5F6001000010008',
    'bf_assets': 'A1B2C3D4E5F6001000010009',
    'bf_info': 'A1B2C3D4E5F600100001000A',
    'bf_photos': 'A1B2C3D4E5F600100001000B',
    'bf_photosui': 'A1B2C3D4E5F600100001000C',

    # PBXFileReference refs (file refs)
    'fr_app': 'A1B2C3D4E5F6002000010001',
    'fr_content': 'A1B2C3D4E5F6002000010002',
    'fr_album': 'A1B2C3D4E5F6002000010003',
    'fr_data': 'A1B2C3D4E5F6002000010004',
    'fr_photoitem': 'A1B2C3D4E5F6002000010005',
    'fr_imageloader': 'A1B2C3D4E5F6002000010006',
    'fr_picker': 'A1B2C3D4E5F6002000010007',
    'fr_sharesheet': 'A1B2C3D4E5F6002000010008',
    'fr_assets': 'A1B2C3D4E5F6002000010009',
    'fr_info': 'A1B2C3D4E5F600200001000A',
    'fr_photos': 'A1B2C3D4E5F600200001000B',
    'fr_photosui': 'A1B2C3D4E5F600200001000C',

    # Groups
    'root_group': 'A1B2C3D4E5F6003000010001',
    'selepic_group': 'A1B2C3D4E5F6003000010002',
    'products_group': 'A1B2C3D4E5F6003000010003',
    'frameworks_group': 'A1B2C3D4E5F6003000010004',

    # Configs
    'project_config_list': 'A1B2C3D4E5F6004000010001',
    'target_config_list': 'A1B2C3D4E5F6004000010002',
    'config_debug': 'A1B2C3D4E5F6004000010003',
    'config_release': 'A1B2C3D4E5F6004000010004',
    'target_config_debug': 'A1B2C3D4E5F6004000010005',
    'target_config_release': 'A1B2C3D4E5F6004000010006',
}

def section(uuid, comment, body):
    return f'\t{uuid} /* {comment} = {{\n\t\tisa = {comment};\n{body}\n\t}};\n'

def empty_props():
    return '\t\tbuildActionMask = 2147483647;\n'

def files_list(uuids):
    lines = '\t\tfiles = (\n'
    for u in uuids:
        lines += f'\t\t\t{u};\n'
    lines += '\t\t);\n'
    return lines

def config_uuids(uuids):
    lines = '\t\tbuildConfigurations = (\n'
    for u in uuids:
        lines += f'\t\t\t{u};\n'
    lines += '\t\t);\n'
    return lines

def build_file_entry(uuid, file_ref, comment):
    return f"""\t{uuid} /* {comment} in Sources */ = {{
\t\tisa = PBXBuildFile;
\t\tfileRef = {file_ref};
\t}};
"""

# ───────────────────────────────────────────
# Build the pbxproj content
# ───────────────────────────────────────────

lines = []
lines.append('// !$*UTF8*$!')
lines.append('{')
lines.append('\tarchiveVersion = 1;')
lines.append('\tclasses = {')
lines.append('\t};')
lines.append('\tobjectVersion = 56;')
lines.append('\tobjects = {')

# ── PBXBuildFile entries ──
lines.append('')
lines.append('/* Begin PBXBuildFile section */')
lines.append(build_file_entry(UUIDS['bf_app'], UUIDS['fr_app'], 'SelePicApp.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_content'], UUIDS['fr_content'], 'ContentView.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_album'], UUIDS['fr_album'], 'AlbumManager.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_data'], UUIDS['fr_data'], 'DataManager.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_photoitem'], UUIDS['fr_photoitem'], 'PhotoItem.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_imageloader'], UUIDS['fr_imageloader'], 'ImageLoader.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_picker'], UUIDS['fr_picker'], 'PhotoPickerView.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_sharesheet'], UUIDS['fr_sharesheet'], 'ShareSheet.swift in Sources'))
lines.append(build_file_entry(UUIDS['bf_assets'], UUIDS['fr_assets'], 'Assets.xcassets in Resources'))
lines.append(build_file_entry(UUIDS['bf_info'], UUIDS['fr_info'], 'Info.plist in Resources'))
lines.append(build_file_entry(UUIDS['bf_photos'], UUIDS['fr_photos'], 'Photos.framework in Frameworks'))
lines.append(build_file_entry(UUIDS['bf_photosui'], UUIDS['fr_photosui'], 'PhotosUI.framework in Frameworks'))
lines.append('/* End PBXBuildFile section */')

# ── PBXFileReference entries ──
lines.append('')
lines.append('/* Begin PBXFileReference section */')
lines.append(f"\t{UUIDS['fr_app']} /* SelePicApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = SelePicApp.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_content']} /* ContentView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ContentView.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_album']} /* AlbumManager.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = AlbumManager.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_data']} /* DataManager.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = DataManager.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_photoitem']} /* PhotoItem.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = PhotoItem.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_imageloader']} /* ImageLoader.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ImageLoader.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_picker']} /* PhotoPickerView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = PhotoPickerView.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_sharesheet']} /* ShareSheet.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ShareSheet.swift; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_assets']} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_info']} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = \\<group\\>; }};")
lines.append(f"\t{UUIDS['fr_photos']} /* Photos.framework */ = {{isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = Photos.framework; path = Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk/System/Library/Frameworks/Photos.framework; sourceTree = SDKROOT; }};")
lines.append(f"\t{UUIDS['fr_photosui']} /* PhotosUI.framework */ = {{isa = PBXFileReference; lastKnownFileType = wrapper.framework; name = PhotosUI.framework; path = Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator.sdk/System/Library/Frameworks/PhotosUI.framework; sourceTree = SDKROOT; }};")
lines.append(f"\t{UUIDS['product_ref']} /* SelePic.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = SelePic.app; sourceTree = BUILT_PRODUCTS_DIR; }};")
lines.append('/* End PBXFileReference section */')

# ── PBXFrameworksBuildPhase ──
lines.append('')
lines.append('/* Begin PBXFrameworksBuildPhase section */')
lines.append('\t' + UUIDS['frameworks_phase'] + ''' /* Frameworks */ = {
\t\tisa = PBXFrameworksBuildPhase;
\t\tbuildActionMask = 2147483647;
\t\tfiles = (
\t\t\t''' + UUIDS['bf_photos'] + ''' /* Photos.framework in Frameworks */,
\t\t\t''' + UUIDS['bf_photosui'] + ''' /* PhotosUI.framework in Frameworks */,
\t\t);
\t\trunOnlyForDeploymentPostprocessing = 0;
\t};''')
lines.append('/* End PBXFrameworksBuildPhase section */')

# ── PBXGroup ──
lines.append('')
lines.append('/* Begin PBXGroup section */')
lines.append('\t' + UUIDS['root_group'] + ''' = {
\t\tisa = PBXGroup;
\t\tchildren = (
\t\t\t''' + UUIDS['selepic_group'] + ''',
\t\t\t''' + UUIDS['frameworks_group'] + ''',
\t\t\t''' + UUIDS['products_group'] + ''',
\t\t);
\t\tsourceTree = "<group>";
\t};''')

lines.append('\t' + UUIDS['selepic_group'] + ''' /* SelePic */ = {
\t\tisa = PBXGroup;
\t\tchildren = (
\t\t\t''' + UUIDS['fr_app'] + ''' /* SelePicApp.swift */,
\t\t\t''' + UUIDS['fr_content'] + ''' /* ContentView.swift */,
\t\t\t''' + UUIDS['fr_album'] + ''' /* AlbumManager.swift */,
\t\t\t''' + UUIDS['fr_data'] + ''' /* DataManager.swift */,
\t\t\t''' + UUIDS['fr_photoitem'] + ''' /* PhotoItem.swift */,
\t\t\t''' + UUIDS['fr_imageloader'] + ''' /* ImageLoader.swift */,
\t\t\t''' + UUIDS['fr_picker'] + ''' /* PhotoPickerView.swift */,
\t\t\t''' + UUIDS['fr_sharesheet'] + ''' /* ShareSheet.swift */,
\t\t\t''' + UUIDS['fr_assets'] + ''' /* Assets.xcassets */,
\t\t\t''' + UUIDS['fr_info'] + ''' /* Info.plist */,
\t\t);
\t\tpath = SelePic;
\t\tsourceTree = "<group>";
\t};''')

lines.append('\t' + UUIDS['frameworks_group'] + ''' /* Frameworks */ = {
\t\tisa = PBXGroup;
\t\tchildren = (
\t\t\t''' + UUIDS['fr_photos'] + ''' /* Photos.framework */,
\t\t\t''' + UUIDS['fr_photosui'] + ''' /* PhotosUI.framework */,
\t\t);
\t\tname = Frameworks;
\t\tsourceTree = "<group>";
\t};''')

lines.append('\t' + UUIDS['products_group'] + ''' /* Products */ = {
\t\tisa = PBXGroup;
\t\tchildren = (
\t\t\t''' + UUIDS['product_ref'] + ''' /* SelePic.app */,
\t\t);
\t\tname = Products;
\t\tsourceTree = "<group>";
\t};''')
lines.append('/* End PBXGroup section */')

# ── PBXNativeTarget ──
lines.append('')
lines.append('/* Begin PBXNativeTarget section */')
lines.append('\t' + UUIDS['target'] + ''' /* SelePic */ = {
\t\tisa = PBXNativeTarget;
\t\tbuildActionMask = 2147483647;
\t\tbuildPhases = (
\t\t\t''' + UUIDS['frameworks_phase'] + ''',
\t\t\t''' + UUIDS['sources_phase'] + ''',
\t\t\t''' + UUIDS['resources_phase'] + ''',
\t\t);
\t\tbuildRules = (
\t\t);
\t\tdependencies = (
\t\t);
\t\tname = SelePic;
\t\tproductInstallPhase = 0;
\t\tproductReference = ''' + UUIDS['product_ref'] + ''' /* SelePic.app */;
\t\tproductType = "com.apple.product-type.application";
\t};''')
lines.append('/* End PBXNativeTarget section */')

# ── PBXProject ──
lines.append('')
lines.append('/* Begin PBXProject section */')
lines.append('\t' + UUIDS['root'] + ''' /* Project object */ = {
\t\tisa = PBXProject;
\t\tattributes = {
\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\tLastSwiftUpdateCheck = 1620;
\t\t\tLastUpgradeCheck = 1620;
\t\t};
\t\tbuildConfigurationList = ''' + UUIDS['project_config_list'] + ''' /* Build configuration list for PBXProject "SelePic" */;
\t\tcompatibilityVersion = "Xcode 14.0";
\t\tcompatibilityVersion = "Xcode 15.0";
\t\tdevelopmentRegion = en;
\t\thasScannedForEncodings = 0;
\t\tknownRegions = (
\t\t\ten,
\t\t\tBase,
\t\t);
\t\tmainGroup = ''' + UUIDS['root_group'] + ''';
\t\tpreferredProjectObjectVersion = 56;
\t\tprojectRoot = "";
\t\ttargets = (
\t\t\t''' + UUIDS['target'] + ''' /* SelePic */,
\t\t);
\t};''')
lines.append('/* End PBXProject section */')

# ── PBXResourcesBuildPhase ──
lines.append('')
lines.append('/* Begin PBXResourcesBuildPhase section */')
lines.append('\t' + UUIDS['resources_phase'] + ''' /* Resources */ = {
\t\tisa = PBXResourcesBuildPhase;
\t\tbuildActionMask = 2147483647;
\t\tfiles = (
\t\t\t''' + UUIDS['bf_assets'] + ''' /* Assets.xcassets in Resources */,
\t\t\t''' + UUIDS['bf_info'] + ''' /* Info.plist in Resources */,
\t\t);
\t\trunOnlyForDeploymentPostprocessing = 0;
\t};''')
lines.append('/* End PBXResourcesBuildPhase section */')

# ── PBXSourcesBuildPhase ──
lines.append('')
lines.append('/* Begin PBXSourcesBuildPhase section */')
lines.append('\t' + UUIDS['sources_phase'] + ''' /* Sources */ = {
\t\tisa = PBXSourcesBuildPhase;
\t\tbuildActionMask = 2147483647;
\t\tfiles = (
\t\t\t''' + UUIDS['bf_app'] + ''' /* SelePicApp.swift in Sources */,
\t\t\t''' + UUIDS['bf_content'] + ''' /* ContentView.swift in Sources */,
\t\t\t''' + UUIDS['bf_album'] + ''' /* AlbumManager.swift in Sources */,
\t\t\t''' + UUIDS['bf_data'] + ''' /* DataManager.swift in Sources */,
\t\t\t''' + UUIDS['bf_photoitem'] + ''' /* PhotoItem.swift in Sources */,
\t\t\t''' + UUIDS['bf_imageloader'] + ''' /* ImageLoader.swift in Sources */,
\t\t\t''' + UUIDS['bf_picker'] + ''' /* PhotoPickerView.swift in Sources */,
\t\t\t''' + UUIDS['bf_sharesheet'] + ''' /* ShareSheet.swift in Sources */,
\t\t);
\t\trunOnlyForDeploymentPostprocessing = 0;
\t};''')
lines.append('/* End PBXSourcesBuildPhase section */')

# ── XCBuildConfiguration (Debug/Release for Project) ──
lines.append('')
lines.append('/* Begin XCBuildConfiguration section */')

# Project Debug config
lines.append('\t' + UUIDS['config_debug'] + ''' /* Debug */ = {
\t\tisa = XCBuildConfiguration;
\t\tbuildSettings = {
\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AUTOMATICALLY;
\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;
\t\t\tCLANG_WARN_COMMA = YES;
\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;
\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
\t\t\tCLANG_WARN_EMPTY_BODY = YES;
\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;
\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;
\t\t\tCLANG_WARN_INT_CONVERSION = YES;
\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;
\t\t\tCLANG_WARN_STRING_CONVERSION = YES;
\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\tCLANG_WARN_UNCERTAIN_DEPRECATED_TYPE = YES;
\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\tCLANG_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\tCLANG_WARN_UNUSED_FUNCTION = YES;
\t\t\tCLANG_WARN_UNUSED_PARAMETER = YES;
\t\t\tCLANG_WARN_UNUSED_VALUE = YES;
\t\t\tCLANG_WARN_UNUSED_VARIABLE = YES;
\t\t\tDEPLOYMENT_TARGET_CLANG_FLAG_DEFAULT = "ios17.0";
\t\t\tDEPLOYMENT_TARGET_CLANG_FLAG_DEPRECATED_PLATFORM = YES;
\t\t\tDEPLOYMENT_TARGET_CLANG_FLAG_UNAVAILABLE_PLATFORM = YES;
\t\t\tDEPLOYMENT_TARGET_LD_FLAG_DEFAULT = "ios17.0";
\t\t\tDSTROOT = "";
\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\tENABLE_TESTABILITY = YES;
\t\t\tENABLE_USER_SCRIPT_SANDBOXING = YES;
\t\t\tGCC_C_LANGUAGE_STANDARD = "gnu17";
\t\t\tGCC_DYNAMIC_NO_PIC = NO;
\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\tGCC_OPTIMIZATION_LEVEL = 0;
\t\t\tGCC_PREPROCESSOR_DEFINITIONS = (
\t\t\t\t"DEBUG=1",
\t\t\t\t"$(inherited)",
\t\t\t);
\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t"$(inherited)",
\t\t\t\t"@executable_path/Frameworks",
\t\t\t);
\t\t\tONLY_ACTIVE_ARCH = YES;
\t\t\tSDKROOT = iphoneos17.5;
\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";
\t\t};
\t\tname = Debug;
\t};''')

# Project Release config
lines.append('\t' + UUIDS['config_release'] + ''' /* Release */ = {
\t\tisa = XCBuildConfiguration;
\t\tbuildSettings = {
\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AUTOMATICALLY;
\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;
\t\t\tCLANG_WARN_COMMA = YES;
\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;
\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
\t\t\tCLANG_WARN_EMPTY_BODY = YES;
\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;
\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;
\t\t\tCLANG_WARN_INT_CONVERSION = YES;
\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;
\t\t\tCLANG_WARN_STRING_CONVERSION = YES;
\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\tCLANG_WARN_UNCERTAIN_DEPRECATED_TYPE = YES;
\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\tCLANG_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\tCLANG_WARN_UNUSED_FUNCTION = YES;
\t\t\tCLANG_WARN_UNUSED_PARAMETER = YES;
\t\t\tCLANG_WARN_UNUSED_VALUE = YES;
\t\t\tCLANG_WARN_UNUSED_VARIABLE = YES;
\t\t\tDEPLOYMENT_TARGET_CLANG_FLAG_DEFAULT = "ios17.0";
\t\t\tDEPLOYMENT_TARGET_CLANG_FLAG_DEPRECATED_PLATFORM = YES;
\t\t\tDEPLOYMENT_TARGET_CLANG_FLAG_UNAVAILABLE_PLATFORM = YES;
\t\t\tDEPLOYMENT_TARGET_LD_FLAG_DEFAULT = "ios17.0";
\t\t\tDEXPECT_MISSING_SIGNATURES = YES;
\t\t\tENABLE_NS_ASSERTIONS = NO;
\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\tGCC_C_LANGUAGE_STANDARD = "gnu17";
\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t"$(inherited)",
\t\t\t\t"@executable_path/Frameworks",
\t\t\t);
\t\t\tSDKROOT = iphoneos17.5;
\t\t\tSUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
\t\t\tSWIFT_COMPILATION_MODE = "wholemodule";
\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Owholemodule";
\t\t};
\t\tname = Release;
\t};''')

# Target Debug config
lines.append('\t' + UUIDS['target_config_debug'] + ''' /* Debug */ = {
\t\tisa = XCBuildConfiguration;
\t\tbuildSettings = {
\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\tDEVELOPMENT_ASSET_PATHS = '"SelePic/Preview Content"';
\t\t\tENABLE_PREVIEWS = YES;
\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\tINFOPLIST_FILE = SelePic/Info.plist;
\t\t\tINFOPLIST_KEY_CFBundleDisplayName = SelePic;
\t\t\tINFOPLIST_KEY UISupportedOrientations = "iphone iPad";
\t\t\tINFOPLIST_KEY_UISupportedOrientations_ipad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\tINFOPLIST_KEY_UISupportedOrientations_iphone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t"$(inherited)",
\t\t\t\t"@executable_path/Frameworks",
\t\t\t);
\t\t\tMARKETING_VERSION = 1.0;
\t\t\tPRODUCT_BUNDLE_IDENTIFIER = comSelePic.app;
\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\tSKIP_INSTALL = NO;
\t\t\tSUPPORTED_DEVICE_FAMILIES = "1,2";
\t\t\tSUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t};
\t\tname = Debug;
\t};''')

# Target Release config
lines.append('\t' + UUIDS['target_config_release'] + ''' /* Release */ = {
\t\tisa = XCBuildConfiguration;
\t\tbuildSettings = {
\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\tDEVELOPMENT_ASSET_PATHS = '"SelePic/Preview Content"';
\t\t\tENABLE_PREVIEWS = YES;
\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\tINFOPLIST_FILE = SelePic/Info.plist;
\t\t\tINFOPLIST_KEY_CFBundleDisplayName = SelePic;
\t\t\tINFOPLIST_KEY UISupportedOrientations = "iphone iPad";
\t\t\tINFOPLIST_KEY_UISupportedOrientations_ipad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\tINFOPLIST_KEY_UISupportedOrientations_iphone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
\t\t\tINFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t"$(inherited)",
\t\t\t\t"@executable_path/Frameworks",
\t\t\t);
\t\t\tMARKETING_VERSION = 1.0;
\t\t\tPRODUCT_BUNDLE_IDENTIFIER = comSelePic.app;
\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\tSKIP_INSTALL = NO;
\t\t\tSUPPORTED_DEVICE_FAMILIES = "1,2";
\t\t\tSUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\tTARGETED_DEVICE_FAMILY = "1,2";
\t\t};
\t\tname = Release;
\t};''')
lines.append('/* End XCBuildConfiguration section */')

# ── XCConfigurationList (Project) ──
lines.append('')
lines.append('/* Begin XCConfigurationList section */')
lines.append('\t' + UUIDS['project_config_list'] + ''' /* Build configuration list for PBXProject "SelePic" */ = {
\t\tisa = XCConfigurationList;
\t\tbuildConfigurations = (
\t\t\t''' + UUIDS['config_debug'] + ''',
\t\t\t''' + UUIDS['config_release'] + ''',
\t\t);
\t\tdefaultConfigurationIsVisible = 0;
\t\tdefaultConfigurationName = Release;
\t};''')

# ── XCConfigurationList (Target) ──
lines.append('\t' + UUIDS['target_config_list'] + ''' /* Build configuration list for PBXNativeTarget "SelePic" */ = {
\t\tisa = XCConfigurationList;
\t\tbuildConfigurations = (
\t\t\t''' + UUIDS['target_config_debug'] + ''',
\t\t\t''' + UUIDS['target_config_release'] + ''',
\t\t);
\t\tdefaultConfigurationIsVisible = 0;
\t\tdefaultConfigurationName = Release;
\t};''')
lines.append('/* End XCConfigurationList section */')

lines.append('')
lines.append('\t};')
lines.append(f'\trootObject = {UUIDS["root"]} /* Project object */;')
lines.append('}')

content = '\n'.join(lines) + '\n'

with open('/Users/scott/aider_Project/SelePic/SelePic.xcodeproj/project.pbxproj', 'w') as f:
    f.write(content)

print("pbxproj written successfully!")
print(f"Total lines: {len(lines)}")

# Verify
opens = content.count('{')
closes = content.count('}')
print(f"Open braces: {opens}, Close braces: {closes}")
assert opens == closes, "BRACE MISMATCH!"
print("Brace check: OK")
