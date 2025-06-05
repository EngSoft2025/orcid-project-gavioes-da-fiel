import * as React from "react";
import { styled } from "@mui/material/styles";
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
  const toggleDrawer = () => {
    setOpen(!open);
  };

  return (
    <Box className="sidebar-container">
      <StyledDrawer variant="permanent" open={open} className="sidebar">
        <Box className="toggle-button-container">
          <div className="sidebarlogo">
            {open && (
              <img
                src="../img/white_logo.png"
                alt="Logo da Plataforma"
                className="logo-img"
              />
            )}
          </div>
          <IconButton onClick={toggleDrawer} className="toggle-button">
            {open ? (
              <ChevronLeftIcon className="icon-white" />
            ) : (
              <MenuIcon className="icon-white" />
            )}
          </IconButton>
        </Box>

        <Box className="sidebar-content">
          {open && data && (
            <>
              <Typography
                variant="h6"
                className="sidebar-title"
                fontWeight={800}
              >
                {data.personal.full_name}
              </Typography>

              {data.personal.urls?.length > 0 && (
                <div>
                  <Typography variant="subtitle2" className="sidebar-subtitle">
                    Site e Links
                  </Typography>
                  {data.personal.urls.map((url, i) => (
                    <Link
                      key={i}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="sidebar-link"
                      color="#fff"
                    >
                      {url}
                    </Link>
                  ))}
                </div>
              )}

              {data.personal.countries?.length > 0 && (
                <div>
                  <Typography variant="subtitle2" className="sidebar-subtitle">
                    Países
                  </Typography>
                  <Typography variant="body2" className="sidebar-text">
                    {data.personal.countries.join(", ")}
                  </Typography>
                </div>
              )}

              {data.keywords?.length > 0 && (
                <div>
                  <Typography variant="subtitle2" className="sidebar-subtitle">
                    Palavras Chaves
                  </Typography>
                  <div className="keyword-container">
                    {data.keywords.map((kw, i) => (
                      <span key={i} className="keyword-item">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {data.personal.external_ids?.length > 0 && (
                <div>
                  <Typography variant="subtitle2" className="sidebar-subtitle">
                    Outras Identificações
                  </Typography>
                  <List dense>
                    {data.personal.external_ids.map((ex, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemText
                          primary={`${ex.type}: ${ex.value}`}
                          className="sidebar-text"
                        />
                      </ListItem>
                    ))}
                  </List>
                </div>
              )}
            </>
          )}
        </Box>
      </StyledDrawer>
    </Box>
  );
}
