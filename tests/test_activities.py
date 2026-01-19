import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club is in the activities list"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
    
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200_on_success(self, client):
        """Test successful signup returns 200"""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to activity"""
        email = "test@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]
    
    def test_signup_returns_success_message(self, client):
        """Test signup returns appropriate message"""
        email = "test@mergington.edu"
        response = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert email in data["message"]
    
    def test_signup_duplicate_returns_400(self, client):
        """Test signing up twice with same email returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup works with email containing special characters"""
        email = "test+tag@mergington.edu"
        response = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_returns_200_on_success(self, client):
        """Test successful unregister returns 200"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_returns_success_message(self, client):
        """Test unregister returns appropriate message"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_not_registered_returns_400(self, client):
        """Test unregistering someone not registered returns 400"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_then_signup_again(self, client):
        """Test that a participant can unregister and sign up again"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify they're in the list
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]


class TestWorkflow:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        email = "newstudent@mergington.edu"
        activity = "Basketball"
        
        # Verify not registered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify registered
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify not registered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_signups_same_student(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multistudent@mergington.edu"
        
        # Sign up for multiple activities
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]
        assert email in activities["Chess Club"]["participants"]
