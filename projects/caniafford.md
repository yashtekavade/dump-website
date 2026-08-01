---
template: project
title: CanIAfford
description: A real cost-of-ownership calculator for bikes and cars in India — EMI, fuel, insurance, and maintenance, checked against your income.
date: 2026-07-31
status: active
tags: [web, nextjs, supabase, typescript]
github: https://github.com/yashtekavade/caniafford
live: https://caniafford-pls.vercel.app/
---

Most EMI calculators only tell you the monthly payment. CanIAfford goes further — it totals up EMI, fuel, insurance, maintenance, and gear against your actual income to answer the real question: can you afford this vehicle, not just the loan on it.

**Stack**

- Next.js frontend, calculator logic ported directly from an Excel model
- Supabase (Postgres + storage) holding vehicle, city-charge, and loan-default data
- Vehicle catalog is fully data-driven — adding a new bike or car is a database insert, no code changes

**Why it's here**

A practical tool solving a real decision problem, and a clean example of shipping a small full-stack app fast: Next.js + Supabase, deployed on Vercel.
