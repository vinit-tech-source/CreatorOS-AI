# AgriLink AI: Project Overview

## 1. Abstract / Executive Summary
AgriLink AI is an advanced, direct farm-to-wholesaler marketplace designed to eliminate traditional agricultural supply chain inefficiencies. In the current ecosystem, middlemen (Adatiyas) extract exorbitant commissions (6% to 12%) while logistical bottlenecks and lack of real-time transit tracking result in significant spoilage rates (25% to 35% for perishables). AgriLink AI solves this by deploying a combination of simulated Computer Vision (YOLOv8 + OpenCV), mathematical modeling (biological kinetics), and financial technology (digital escrow) to create a transparent, zero-commission, and highly efficient agricultural marketplace.

## 2. Problem Statement
The agricultural supply chain faces three critical challenges:
1. **Middleman Exploitation**: Farmers are heavily dependent on local commission agents who manipulate spot prices and charge heavy fees, drastically reducing farm-gate profitability.
2. **High Spoilage & Wastage**: A lack of scientific shelf-life monitoring during transit means a substantial percentage of perishable crops rot before reaching the wholesaler.
3. **Logistical Friction**: Arranging and paying for transportation is a burden for individual farmers, leading to delays and increased overhead costs.

## 3. Proposed Architecture & Core Modules
The system is divided into several interconnected modules:

### 3.1. AI-Powered Visual Grading System
Before listing a crop, farmers upload a photograph. The system utilizes a simulated 3-step neural network pipeline:
*   **Segmentation**: Identifies the crop bounds using YOLOv8.
*   **Color Histogram Analysis**: Assesses the ripeness of the produce based on color thresholds.
*   **Defect Detection**: Uses a PyTorch CNN to detect surface bruises.
This pipeline outputs an **Initial Visual Purity Grade ($F_0$)**, ensuring standardized quality metrics for buyers without manual inspection.

### 3.2. Biological Kinetics Spoilage Engine
To address transit spoilage, the platform integrates a mathematical model that tracks the real-time decay of produce.
*   **Formula**: $F(t) = F_0 \times e^{-\lambda t}$
*   **Variables**: 
    *   $F_0$: Initial Visual Grade (derived from AI).
    *   $\Delta t$: Hours elapsed since harvest.
    *   $\lambda$: Biological decay constant, dynamically modified by the ratio of ambient transit temperature ($T_{env}$) to optimal temperature ($T_{opt}$) based on the Arrhenius equation.
This engine allows wholesalers to filter inventory by biological urgency and remaining shelf-life.

### 3.3. Financial & Logistics Escrow System
The platform introduces a **50/50 logistics cost split** between the farmer and the wholesaler, making transportation equitable.
*   **Digital Escrow**: Powered by Razorpay Route architecture, the system locks the gross crop value plus 100% of the transport cost.
*   **Upfront Logistics Payout**: The escrow releases 100% of the freight cash advance directly to local village drivers, removing out-of-pocket expenses for the farmer while maintaining trust.

### 3.4. IoT Telematics & Fleet Tracking
The platform provides a live simulated dashboard for wholesalers to track in-transit reefer trucks. It integrates mock live GPS data alongside real-time Temperature and Humidity dials, which feed directly into the biological kinetics engine to continually update the $F(t)$ score.

### 3.5. Farmer Support & AI Assistant
*   **Govt Scheme Wizard**: Interactive eligibility checks for subsidies like PM-KISAN, PMFBY, and AIF, utilizing mocked land records (7/12 extracts).
*   **Multilingual Chatbot**: An edge AI assistant capable of local language communication, fetching eNAM market rates, and offering diagnostic advice for crop diseases based on uploaded images.

## 4. Technical Stack
The platform is developed as a modern Single Page Application (SPA):
*   **Frontend Framework**: React 19 utilizing Vite as the bundler.
*   **Language**: TypeScript for strong typing and error reduction.
*   **Styling**: Tailwind CSS (v4) emphasizing modern Glassmorphism aesthetics and token-based design.
*   **Simulated AI/ML Layer**: Front-end mathematical simulation mimicking the behavior of PyTorch, OpenCV, and YOLOv8 models.

## 5. Conclusion & Innovations for Survey Paper
For academic and survey purposes, AgriLink AI demonstrates the integration of theoretical physics (kinetics) and computer science (edge AI) into a traditional socioeconomic domain (agriculture). By replacing arbitrary human grading with algorithmic visual assessment and static transportation with dynamic, temperature-aware decay tracking, the project offers a blueprint for drastically reducing post-harvest losses and improving the economic welfare of smallholder farmers.
