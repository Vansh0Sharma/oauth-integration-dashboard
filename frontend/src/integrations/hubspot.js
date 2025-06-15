// src/integrations/hubspot.js

import { useState } from 'react';
import {
    Box,
    Button,
} from '@mui/material';
import axios from 'axios';

const HUBSPOT_BASE = "http://localhost:8000/integrations/hubspot";

export const HubspotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [authComplete, setAuthComplete] = useState(false);

    const handleAuthorize = async () => {
        try {
            const formData = new FormData();
            formData.append("user_id", user);
            formData.append("org_id", org);

            const response = await axios.post(`${HUBSPOT_BASE}/authorize`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            if (response.data?.url) {
                window.location.href = response.data.url;
            } else {
                alert("Authorization URL not returned.");
            }
        } catch (err) {
            console.error("Authorization error:", err);
            alert("Failed to start authorization.");
        }
    };

    const handleGetCredentials = async () => {
        try {
            const formData = new FormData();
            formData.append("user_id", user);
            formData.append("org_id", org);

            const response = await axios.post(`${HUBSPOT_BASE}/credentials`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setIntegrationParams({
                type: 'Hubspot',
                credentials: response.data,
            });
            setAuthComplete(true);
        } catch (err) {
            console.error("Credential fetch error:", err);
            alert("Failed to retrieve credentials.");
        }
    };

    return (
        <Box display='flex' flexDirection='column' sx={{ mt: 2 }}>
            <Button
                variant="contained"
                onClick={handleAuthorize}
                sx={{ mb: 1 }}
            >
                Authorize HubSpot
            </Button>
            <Button
                variant="contained"
                onClick={handleGetCredentials}
                disabled={authComplete}
            >
                Get HubSpot Credentials
            </Button>
        </Box>
    );
};
