# Tariff Calculator

A web-based application for calculating and analyzing tariff impacts on international trade. This tool helps users understand how tariffs affect product pricing and trade economics.

## 📋 Project Summary

The Tariff Calculator is an interactive web application designed to help businesses, economists, and policymakers analyze the economic impact of tariffs on imported goods. It provides real-time calculations and visualizations to better understand trade costs and pricing strategies.

## ✨ Features

- **Tariff Calculation Engine**: Calculate customs duties and import taxes based on product categories and countries
- **Interactive Web Interface**: User-friendly interface for inputting product and tariff data
- **Multi-Currency Support**: Handle calculations in various currencies with real-time conversion
- **Product Categories**: Support for different HS (Harmonized System) codes and product classifications
- **Data Visualization**: Charts and graphs to visualize tariff impacts
- **Export Functionality**: Download calculation results for reporting and analysis
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v14.0 or higher)
- **npm** (v6.0 or higher) or **yarn**
- A modern web browser (Chrome, Firefox, Safari, or Edge)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/JohnTan38/tariff.git
   cd tariff

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install

3. **Set up environment variables**
   ```bash
   cp .env.example .env
      Edit, add your configuration:
   PORT=3000
   API_KEY=your_api_key_here
   DATABASE_URL=your_database_url

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev

5. **Open your browser**
   ```bash
   Navigate to http://localhost:3000

   Production Build
   ```bash
   npm run build
   npm start
   # or
   yarn build
   yarn start

## 📖 Usage
Enter Product Details: Input the product description, value, and country of origin
Select Tariff Rates: Choose applicable tariff rates based on trade agreements
Calculate: Click the calculate button to see the total landed cost

View Results: Review the breakdown of duties, taxes, and total costs
Export: Download your results as PDF or CSV

## 🛠️ Technology Stack
Frontend: HTML5, CSS3, JavaScript (ES6+)
Backend: Node.js, Express
Database: MongoDB / PostgreSQL
APIs: Customs data APIs, Currency conversion APIs
Build Tools: Webpack / Vite

## 📁 Project Structure
```bash
tariff/
├── public/           # Static assets
├── src/
│   ├── components/   # Reusable UI components
│   ├── utils/        # Utility functions
│   ├── api/          # API integration
│   └── styles/       # CSS/SCSS files
├── tests/            # Test files
├── .env.example      # Environment variables template
├── package.json      # Project dependencies
└── README.md         # This file


## 🧪 Testing

Run the test suite:

```bash
npm test
# or
yarn test


📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
JohnTan38

GitHub: @JohnTan38

🙏 Acknowledgments
Trade data provided by customs authorities
Currency conversion APIs
Open-source community for various libraries and tools
📞 Support
For support, please open an issue in the GitHub repository or contact the maintainer.

Note: This project is for educational and informational purposes. Always consult with customs authorities and trade professionals for official tariff information.
 
