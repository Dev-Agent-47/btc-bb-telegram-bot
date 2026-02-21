from flask import Flask, request, render_template_string
import json

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Crypto Alert Bot</title>
<h2>📊 Crypto Alert Bot</h2>

<form method="post">
  Symbol:<br>
  <select name="symbol">
    <option value="BTC-USD">BTC</option>
    <option value="ETH-USD">ETH</option>
  </select><br><br>

  Timeframe (min):<br>
  <input type="number" name="timeframe" min="1"><br><br>

  BB Length:<br>
  <input type="number" name="bb_length" min="5"><br><br>

  <button type="submit">Save Settings</button>
</form>

<p>{{ msg }}</p>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    if request.method == "POST":
        config = {
            "symbol": request.form["symbol"],
            "timeframe": int(request.form["timeframe"]),
            "bb_length": int(request.form["bb_length"])
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        msg = "✅ Settings saved. Will apply next candle."

    return render_template_string(HTML, msg=msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
