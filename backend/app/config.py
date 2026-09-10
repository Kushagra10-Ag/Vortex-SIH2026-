class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:viduit1234@localhost:5432/bizmate"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "secret-key"
    JWT_SECRET_KEY = "super-secret-key"