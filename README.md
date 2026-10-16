# CodeLens AI — AI-Powered Codebase Intelligence Platform

> Understand unfamiliar codebases faster with AI-powered code search, repository exploration, and context-aware question answering.

CodeLens AI is an AI-powered developer platform designed to help developers understand, navigate, and analyze software repositories. It combines a React and TypeScript frontend with a Python backend, AI/LLM components, and code-analysis modules to provide a unified interface for exploring source code.

The platform is designed around a simple workflow: explore a repository, ask questions about its implementation, inspect relevant source files, and understand how different parts of the codebase work together.

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Application Workflow](#application-workflow)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [AI and LLM Pipeline](#ai-and-llm-pipeline)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Docker Deployment](#docker-deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Security Considerations](#security-considerations)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Modern software projects often contain hundreds or thousands of files distributed across multiple modules, services, and layers. Understanding how authentication, business logic, APIs, database operations, and internal dependencies interact can require substantial manual investigation.

CodeLens AI aims to simplify this process by providing an intelligent interface for codebase exploration.

Instead of manually searching through files, developers can use a conversational interface to investigate implementation details and inspect relevant code through a structured file explorer and code viewer.

The project combines:

- Full-stack application development.
- AI and Large Language Model integration.
- Code analysis and repository exploration.
- Retrieval-Augmented Generation (RAG) concepts.
- Modular backend architecture.
- Containerized development and deployment.

The architecture is designed to support future extensions such as semantic code search, code dependency analysis, repository indexing, and source-grounded AI answers.

## Problem Statement

Developers frequently encounter challenges when working with unfamiliar codebases:

- Finding the correct implementation across multiple files.
- Understanding relationships between classes, functions, and modules.
- Tracing request flows through backend services.
- Identifying where specific business logic is implemented.
- Understanding complex code without extensive manual investigation.
- Navigating large repositories efficiently.

Traditional text search can locate matching keywords but may not explain how different components interact or how a particular feature is implemented.

CodeLens AI aims to address these challenges by combining repository navigation, code analysis, and AI-assisted code understanding in one developer-focused platform.

## Objectives

The primary objectives of CodeLens AI are:

1. Build an intuitive interface for exploring software repositories.
2. Provide a conversational interface for code-related questions.
3. Organize source code into navigable files and readable code views.
4. Integrate AI capabilities into the developer workflow.
5. Develop a modular backend that separates APIs, services, AI logic, and code analysis.
6. Support maintainable development through testing, configuration management, and containerization.
7. Establish a foundation for retrieval-based code understanding and scalable repository indexing.

---

## Key Features

The following describes the platform's intended capabilities. Verify each feature against the current implementation before presenting it as completed.

### 1. AI-Powered Codebase Assistant

A conversational interface for asking questions about a software repository.

Example questions:

- How does authentication work in this project?
- Where is the business logic for a particular operation?
- Which module handles API requests?
- Explain the execution flow of this function.
- What changes might be required to modify a particular feature?

The AI layer is intended to use relevant repository context to produce more useful and implementation-specific answers.

### 2. Interactive Chat Interface

The frontend includes a dedicated `ChatPanel.tsx` component.

This component provides the foundation for a developer-oriented chat experience, including question submission and presentation of AI responses.

### 3. Source Code Viewer

The `CodeViewer.tsx` component provides the frontend structure for displaying source code.

The code viewer can serve as the interface for inspecting implementations, reviewing relevant snippets, and connecting AI explanations to actual source files.

### 4. Repository File Explorer

The `FileTree.tsx` component provides the foundation for hierarchical file navigation.

This enables developers to browse repository files and locate the source code they want to understand.

### 5. Authentication Interface

The frontend contains separate login and registration pages:

- `Login.tsx`
- `Register.tsx`

These provide the UI foundation for user authentication. Actual authentication behavior depends on the backend integration and must be verified separately.

### 6. Modular AI and Code Analysis

The backend separates AI-related functionality and code analysis into dedicated packages.

This organization allows AI workflows, repository analysis, API handlers, and supporting services to evolve independently.

### 7. Containerized Infrastructure

The repository includes Dockerfiles and a Docker Compose configuration.

These provide the foundation for packaging application components and managing supporting services in a reproducible development environment.

---

## System Architecture

CodeLens AI follows a modular full-stack architecture.

```text
                  Developer
                      |
                      v
          React + TypeScript Frontend
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Chat UI     File Tree   Code Viewer
          |           |           |
          +-----------+-----------+
                      |
                      v
                Backend API
                  FastAPI
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       AI / LLM   Code Analysis  Core Services
          |           |           |
          +-----------+-----------+
                      |
                      v
            Data and Infrastructure
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Database   AI Resources   Background
                                 Workers
