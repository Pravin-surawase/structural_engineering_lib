# Core

**Type:** Python Package
**Last Updated:** 2026-08-17
**Files:** 23

## Public API

- `DesignCode`
- `FlexureDesigner`
- `ShearDesigner`
- `DetailingRules`
- `Concrete`
- `Steel`
- `MaterialFactory`
- `Section`
- `RectangularSection`
- `TSection`
- `LSection`
- `CodeRegistry`
- `BuildingModelV1`
- `BuildingSourceRecordV1`
- `ExcludedGravityActionV1`
- `GravityActionCategoryV1`
- `GravityApprovedExclusionV1`
- `GravityCombinationFactorV1`
- `GravityCombinationV1`
- `GravityFootingDestinationV1`

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [__init__.py](__init__.py) | Core module - Code-agnostic base classes and utilities. | 0 | 0 | 122 |
| [base.py](base.py) | Abstract base classes for design code implementations. | 5 | 0 | 139 |
| [building_gravity.py](building_gravity.py) | Versioned physical-model and load-basis contracts for gravit | 15 | 2 | 686 |
| [constants.py](constants.py) | Module:       constants | 0 | 0 | 20 |
| [data_types.py](data_types.py) | Module:       types | 15 | 0 | 2143 |
| [deprecation.py](deprecation.py) | Module:       deprecation | 0 | 2 | 156 |
| [error_messages.py](error_messages.py) | Module:       error_messages | 0 | 15 | 496 |
| [errors.py](errors.py) | Module:       errors | 11 | 1 | 884 |
| [geometry.py](geometry.py) | Code-agnostic geometry definitions. | 4 | 2 | 254 |
| [gravity_workflow.py](gravity_workflow.py) | Versioned request, applicability, action, and result types f | 12 | 0 | 310 |
| [inputs.py](inputs.py) | Module:       inputs | 6 | 3 | 635 |
| [logging_config.py](logging_config.py) | Module:       logging_config | 0 | 1 | 66 |
| [materials.py](materials.py) | Code-agnostic material models. | 3 | 0 | 159 |
| [models.py](models.py) | Canonical Data Models for Structural Engineering Library. | 11 | 0 | 554 |
| [numerics.py](numerics.py) | Numeric safety utilities for structural calculations. | 0 | 3 | 78 |
| [registry.py](registry.py) | Design code registry for multi-code support. | 1 | 1 | 98 |
| [result_base.py](result_base.py) | Module:       result_base | 3 | 0 | 191 |
| [result_contract.py](result_contract.py) | Canonical, fail-closed structural result and issue contract. | 9 | 2 | 266 |
| [source_identity.py](source_identity.py) | Layer-neutral identities for the exact controlled IS 456 sou | 0 | 0 | 13 |
| [types.py](types.py) | Compatibility shim for the renamed data_types module. | 0 | 0 | 51 |
| [utilities.py](utilities.py) | Module:       utilities | 0 | 4 | 70 |
| [validation.py](validation.py) | Module:       validation | 0 | 13 | 643 |
| [version.py](version.py) | Runtime package-version identity without source/installation | 1 | 2 | 123 |
