import * as React from "react";
import { styled, useTheme } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import MenuIcon from "@mui/icons-material/Menu";
import "./Sidebar.css";

const drawerWidth = 300;
const closedWidth = 60;

const openedMixin = (theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: "hidden",
});

const closedMixin = (theme) => ({
  width: closedWidth,
  transition: theme.transitions.create("width", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: "hidden",
});

const StyledDrawer = styled(Drawer, {
  shouldForwardProp: (prop) => prop !== "open",
})(({ theme, open }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: "nowrap",
  boxSizing: "border-box",
  position: "relative",
  ...(open && {
    ...openedMixin(theme),
    "& .MuiDrawer-paper": {
      ...openedMixin(theme),
      position: "relative",
      height: "100%",
    },
  }),
  ...(!open && {
    ...closedMixin(theme),
    "& .MuiDrawer-paper": {
      ...closedMixin(theme),
      position: "relative",
      height: "100%",
    },
  }),
}));

export default function Sidebar({ open, setOpen, data }) {
  const theme = useTheme();

  const toggleDrawer = () => {
    setOpen(!open);
  };

  return (
    <Box sx={{ display: "flex", height: "100%" }}>
      <StyledDrawer variant="permanent" open={open} className="sidebar">
        <Box className="toggle-button-container">
          <div className="sidebarlogo">
            {open && (
              <img
                src="../img/logo.png"
                alt="Logo da Plataforma"
                className="logo-img"
              />
            )}
          </div>
          <IconButton onClick={toggleDrawer} className="toggle-button">
            {open ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
        </Box>

        <Box className="sidebar-content">
          {open && data && (
            <>
              <Typography variant="h6" sx={{ color: "#e2e8f0", mb: 1 }}>
                {data.personal.full_name}
              </Typography>

              {data.personal.urls?.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ color: "#94a3b8", fontWeight: 500 }}
                  >
                    Site e Links
                  </Typography>
                  {data.personal.urls.map((url, i) => (
                    <Link
                      key={i}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{
                        color: "#60a5fa",
                        display: "block",
                        wordBreak: "break-all",
                        mt: 0.5,
                      }}
                    >
                      {url}
                    </Link>
                  ))}
                </Box>
              )}

              {data.personal.countries?.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ color: "#94a3b8", fontWeight: 500 }}
                  >
                    Países
                  </Typography>
                  <Typography variant="body2" sx={{ color: "#e2e8f0" }}>
                    {data.personal.countries.join(", ")}
                  </Typography>
                </Box>
              )}

              {data.keywords?.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ color: "#94a3b8", fontWeight: 500 }}
                  >
                    Palavras Chaves
                  </Typography>
                  <Box
                    sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}
                  >
                    {data.keywords.map((kw, i) => (
                      <Box
                        key={i}
                        sx={{
                          backgroundColor: "#334155",
                          color: "#e2e8f0",
                          borderRadius: "12px",
                          px: 1.5,
                          py: 0.5,
                          fontSize: "0.75rem",
                          fontWeight: 500,
                        }}
                      >
                        {kw}
                      </Box>
                    ))}
                  </Box>
                </Box>
              )}

              {data.personal.external_ids?.length > 0 && (
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ color: "#94a3b8", fontWeight: 500 }}
                  >
                    Outras Identificações
                  </Typography>
                  <List dense>
                    {data.personal.external_ids.map((ex, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemText
                          primary={`${ex.type}: ${ex.value}`}
                          primaryTypographyProps={{ sx: { color: "#e2e8f0" } }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </>
          )}
        </Box>
      </StyledDrawer>
    </Box>
  );
}
