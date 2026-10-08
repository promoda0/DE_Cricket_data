# Raw/Bronze Ingestion Contract

## 1. Purpose

This document defines the contract for ingesting Cricket match JSON
files from the source system into the Raw/Bronze layer.

The Bronze layer is responsible for preserving source data and making
it available for downstream processing.

Business transformations are not part of the Bronze layer.

---

## 2. Source Contract

### Source System

Local development source:

G:\My Drive\Cricket\ipl

Production equivalent:

Object storage such as Amazon S3, Azure Data Lake Storage, or Google
Cloud Storage.

### Input Format

- File format: JSON
- Expected root type: JSON object
- One match per JSON file
- Source filename must be preserved

Example:

1082591.json

---

## 3. Data Flow

```text
Cricket JSON Source
        |
        v
     Bronze
        |
        v
     Silver
        |
        v
      Gold