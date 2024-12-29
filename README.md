# Twitter Trends Scraper with Flask and Selenium

This is a Flask-based web application that scrapes Twitter (now X) trends using Selenium WebDriver, stores the data in MongoDB, and provides an interface for running the scraping script. It can be run on a server, and the trends are fetched periodically and stored for analysis or reporting.

## Features

- Scrapes Twitter trends after logging in via Selenium WebDriver.
- Uses headless Chrome for automation (suitable for Docker or cloud environments).
- Stores scraped trends and metadata (unique ID, IP address, timestamp) in MongoDB.
- Exposes an API endpoint (`/run-script`) to trigger the scraping process.
- Displays the trends via a web interface using Flask.

## Requirements

- **Python 3.11+**
- **Chromium**: For running Selenium WebDriver in headless mode.
- **MongoDB**: For storing scraped data.

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/twitter-trends-scraper.git
   cd twitter-trends-scraper
   ```

2. **Install Python Dependencies:**

   First, create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/macOS
   venv\Scripts\activate  # For Windows
   ```

   Then, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables:**

   Create a `.env` file in the root directory and define the following environment variables:

   ```ini
   TWITTER_USERNAME=<your-twitter-username>
   TWITTER_PASSWORD=<your-twitter-password>
   TWITTER_PHONE=<your-phone-or-email>
   MONGODB_URI=<your-mongodb-uri>
   ```

4. **Docker Setup (Optional):**

   If you want to run this app inside a Docker container, you can build the Docker image and run it as follows:

   ```bash
   docker build -t twitter-trends-scraper .
   docker run -p 5000:5000 twitter-trends-scraper
   ```

   This will start the Flask app inside the container, which will be accessible at `http://localhost:5000`.

## Running the Application

After setting up the environment, you can run the Flask application locally:

```bash
python app/app.py
```

The application will be available at `http://localhost:5000`. You can visit the homepage to check the trends and trigger the scraping process by visiting the `/run-script` endpoint.

## API Endpoints

- **GET `/`**: Displays the web interface with the option to trigger the scraping.
- **GET `/run-script`**: Triggers the script that scrapes Twitter trends and stores them in MongoDB. Returns the unique ID, trends, and IP address as a JSON response.

## Dockerfile

The project comes with a pre-configured Dockerfile for easy containerization. The Dockerfile installs all necessary dependencies, sets up the working directory, and runs the Flask app in a containerized environment.


## Troubleshooting

1. **Chromium WebDriver Issues**: Make sure the `chromium` and `chromium-driver` are correctly installed. You may need to adjust the path to the ChromeDriver or update your system dependencies.

2. **MongoDB Connection**: Ensure that MongoDB is running and that the connection string in the `.env` file is correct. If using a remote database, make sure your IP address is whitelisted.

3. **Twitter Login Issues**: The script uses Selenium to simulate logging into Twitter. Make sure your credentials are valid, and check if Twitter has introduced any changes that might affect the login flow.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Selenium WebDriver](https://www.selenium.dev/)
- [MongoDB](https://www.mongodb.com/)
- [Chromium WebDriver](https://www.chromium.org/)

---

Feel free to contribute, open issues, or create pull requests for enhancements.
