# Realm Operations Test Fixes - Summary

## Overview

Fixed all 5 skipped tests in `test_realm_operations.py` that were failing due to incorrect API endpoint paths. After giving the test-admin user 'admin' realm role, all realm management operations now work correctly.

## Issues Fixed

### 1. **test_list_realms** - FIXED ✅
**Problem:** Using wrong endpoint path
- **Before:** `GET /admin/` (resulted in HTTP 302 redirect)
- **After:** `GET /admin/realms` (returns HTTP 200 OK)
- **File:** `src/tools/realm_operations_tools.py:226`

### 2. **test_realm_lifecycle** - FIXED ✅
**Problem:** Using wrong endpoint for realm creation
- **Before:** `POST /admin/` (resulted in HTTP 405 Method Not Allowed)
- **After:** `POST /admin/realms` (returns HTTP 201 Created)
- **File:** `src/tools/realm_operations_tools.py:47`

### 3. **test_import_realm** - FIXED ✅
**Problem:** Using wrong endpoint for realm import
- **Before:** `POST /admin/` (resulted in HTTP 405 Method Not Allowed)
- **After:** `POST /admin/realms` (returns HTTP 201 Created)
- **File:** `src/tools/realm_operations_tools.py:111`

### 4. **test_backup_and_restore_realm** - FIXED ✅
**Problem:** Restore uses import which had wrong endpoint (same as #3)
- **After:** Restore now works correctly with proper endpoint

### 5. **test_partial_import_realm** - FIXED ✅
**Problem:** Test was using wrong parameter names
- **Before:** `realm_data` and `if_resource_exists` parameters
- **After:** `import_data` parameter (matching function signature)
- **File:** `tests/test_realm_operations.py:237-241`

### 6. **test_duplicate_realm** - FIXED ✅
**Problems:**
- Test was using wrong parameter names (`new_realm_name` instead of `target_realm_name`)
- Export included `defaultRole` object with source realm references causing 409 Conflict

**Fixes:**
- Updated test to use correct parameter names
- Modified `duplicate_realm` to remove `defaultRole` from export (Keycloak auto-generates it)
- Removed default system clients to avoid conflicts
- **Files:**
  - `tests/test_realm_operations.py:271-288`
  - `src/tools/realm_operations_tools.py:263-289`

### 7. **delete_realm** - FIXED ✅
**Problem:** Using wrong endpoint for realm deletion
- **Before:** `DELETE /` with `realm=realm_name` (constructed incorrect URL)
- **After:** `DELETE /realms/{realm_name}` with `skip_realm=True`
- **File:** `src/tools/realm_operations_tools.py:81`

## Root Cause Analysis

All issues were caused by incorrect endpoint path construction in the `realm_operations_tools.py` file. The functions were using:
- `endpoint="/"` with `skip_realm=True` → resulted in `/admin/` (WRONG)

Should have been using:
- `endpoint="/realms"` with `skip_realm=True` → results in `/admin/realms` (CORRECT)

The Keycloak Admin REST API documentation confirms:
- **List realms:** `GET /admin/realms`
- **Create realm:** `POST /admin/realms`
- **Delete realm:** `DELETE /admin/realms/{realm}`

## Test Results

### Before Fix
- **8 Realm Operation Tests:** 3 passed, 5 skipped (due to HTTP 405 errors)
- **15 Total Tests:** 10 passed, 5 skipped

### After Fix
- **8 Realm Operation Tests:** 8 passed ✅ (100% pass rate)
- **15 Total Tests:** 15 passed ✅ (100% pass rate)

### Consistency Verification
Ran tests twice to verify idempotent results and proper cleanup:
- **Run 1:** 15 passed in 7.49s
- **Run 2:** 15 passed in 7.47s

✅ **No test data pollution - all cleanup successful!**

## Files Modified

### Source Code
1. **src/tools/realm_operations_tools.py**
   - `list_realms()` - line 226: Changed endpoint from `/` to `/realms`
   - `create_realm()` - line 47: Changed endpoint from `/` to `/realms`
   - `delete_realm()` - line 81: Changed to use `/realms/{realm_name}` with `skip_realm=True`
   - `import_realm()` - line 111: Changed endpoint from `/` to `/realms`
   - `duplicate_realm()` - lines 263-289: Added removal of `defaultRole` and default clients

### Test Files
2. **tests/test_realm_operations.py**
   - `test_partial_import_realm()` - lines 237-241: Fixed parameter names
   - `test_duplicate_realm()` - lines 271-288: Fixed parameter names and assertions
   - Added cleanup at start of `test_duplicate_realm` to handle leftover data

## API Coverage Impact

With these fixes, the Realm Management API coverage is now complete:
- ✅ List realms
- ✅ Create realm
- ✅ Delete realm
- ✅ Import realm (full)
- ✅ Import realm (partial)
- ✅ Export realm (full)
- ✅ Export realm (partial)
- ✅ Backup realm
- ✅ Restore realm
- ✅ Duplicate realm

## Testing Best Practices Applied

Following the guidelines from CLAUDE.md:
1. ✅ **100% Pass Rate** - All tests pass completely
2. ✅ **Run Tests Twice** - Verified consistent idempotent results
3. ✅ **Proper Cleanup** - No test data pollution between runs
4. ✅ **Idempotent Fixtures** - Tests handle existing resources gracefully

## Permissions Required

For these tests to pass, the test user needs:
- **Realm Role:** `admin` (in master realm)
- This grants full realm management permissions including:
  - Creating new realms
  - Deleting realms
  - Importing/exporting realm configurations
  - Managing realm resources

## Next Steps

All realm operation tests are now passing! The codebase has:
- Correct Keycloak Admin REST API endpoint paths
- Proper test parameter names matching function signatures
- Idempotent test fixtures with cleanup
- 100% consistent test results across multiple runs
