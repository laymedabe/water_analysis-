import "./globals.css";

export const metadata = {
  title: "WQI Prediction Dashboard",
  description: "Machine Learning Water Quality Index Predictor via Neural Networks",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
