import sys
try:
    from app.main import app
    print("Successfully imported app.main")
except Exception as e:
    import traceback
    traceback.print_exc()
