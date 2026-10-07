# Cricket Data Engineering Project

## 1. Project Overview

This project is a production-oriented Data Engineering simulation built around
cricket match data.

The objective is to design and implement an end-to-end data platform that
ingests raw cricket match data, transforms it into structured datasets, and
produces analytics-ready data for business and analytical use cases.

The project is intentionally developed incrementally to simulate a real
Data Engineering development lifecycle.

---

## 2. Business Domain

**Domain:** Cricket / Sports Analytics

The source data contains cricket match information, including match metadata,
teams, venues, innings, overs, deliveries, runs, wickets, and other match-level
information.

The initial business requirement is to make important match-level information
available in structured form, including:

- Match information
- Venue
- Innings information
- First innings score
- Second innings score
- Total match score

The data model and pipeline will evolve as additional business requirements
are introduced.

---

## 3. Data Source

The project currently uses cricket match JSON files obtained from Cricsheet.

The local development source is mounted through Google Drive for Desktop.

Example source location:

```text
G:\My Drive\Cricket\ipl

Recent ticket number you can below link sheets link.
https://docs.google.com/spreadsheets/d/1cN0hNOy3FtIBCGChitx7xwmqOHgyefFTRXyVGDACGW8/edit?gid=0#gid=0
