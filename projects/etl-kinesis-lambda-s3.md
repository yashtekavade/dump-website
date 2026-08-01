---
template: project
title: "ETL Pipeline: Kinesis → Lambda → S3"
description: A streaming ETL pipeline — Amazon Kinesis Data Stream feeds AWS Lambda, which lands processed records in S3.
date: 2025-07-25
status: archived
tags: [aws, python, etl]
github: https://github.com/yashtekavade/etl_kinesis_lambda_s3
live:
---

A focused streaming ETL project: sensor-style JSON records are generated and pushed into a Kinesis Data Stream, a Lambda function consumes each batch, decodes and parses it, and writes the result to S3 as individual JSON files.

**Architecture**

Cognito-authenticated Kinesis Data Generator → Kinesis Data Stream → Lambda (batch size 100) → S3, with the Cognito user and permissions provisioned via a CloudFormation template.

**Why it's here**

A clean, minimal reference for the core pattern behind a lot of streaming ETL work — useful as the simplest version of the same idea scaled up in the Pizza Chain and Media Stream projects.
