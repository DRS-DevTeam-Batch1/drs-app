# Forwarding to another module
        trajectory_api = "http://localhost:5001/analyze_trajectory"
        response = requests.post(trajectory_api, json=output_payload)
        print("Forwarded to trajectory module. Response:", response.text)

        return jsonify({
            "status": "success",
            "bat_edge_detected": detection["bat_edge_detected"],
            "forwarded_to_trajectory": True,
            "trajectory_module_response": response.json()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)