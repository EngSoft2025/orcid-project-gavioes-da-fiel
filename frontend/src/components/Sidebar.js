import * as React from 'react';
import { styled, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import IconButton from '@mui/material/IconButton';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import MenuIcon from '@mui/icons-material/Menu';
import InsertChartIcon from '@mui/icons-material/InsertChart';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Divider from '@mui/material/Divider';
import "./Sidebar.css"

const drawerWidth = 300;
const closedWidth = 60;

const openedMixin = (theme) => ({
  width: drawerWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
});

const closedMixin = (theme) => ({
  width: closedWidth,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
});

const StyledDrawer = styled(Drawer, {
  shouldForwardProp: (prop) => prop !== 'open',
})(({ theme, open }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: 'nowrap',
  boxSizing: 'border-box',
  position: 'relative',
  ...(open && {
    ...openedMixin(theme),
    '& .MuiDrawer-paper': {
      ...openedMixin(theme),
      position: 'relative',
      height: '100%',
    },
  }),
  ...(!open && {
    ...closedMixin(theme),
    '& .MuiDrawer-paper': {
      ...closedMixin(theme),
      position: 'relative',
      height: '100%',
    },
  }),
}));

export default function Sidebar({ open, setOpen, data }) {
  const theme = useTheme();

  const toggleDrawer = () => {
    setOpen(!open);
  };

  return (
    <Box sx={{ display: 'flex', height: '100%' }}>
    

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
              <Typography variant="h6" gutterBottom>
                {data.personal.full_name}
              </Typography>

              {data.keywords?.length > 0 && (
                <div className="sidebar-section">
                  <Typography variant="subtitle2" gutterBottom>
                    Palavras-chave
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {data.keywords.map((kw, i) => (
                      <Typography key={i} variant="body2" component="span">
                        {kw}
                      </Typography>
                    ))}
                  </Box>
                  <Divider sx={{ my: 1 }} />
                </div>
              )}

              {data.personal.other_names?.length > 0 && (
                <div className="sidebar-section">
                  <Typography variant="subtitle2" gutterBottom>
                    Outros nomes
                  </Typography>
                  <List dense>
                    {data.personal.other_names.map((n, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemText primary={n} />
                      </ListItem>
                    ))}
                  </List>
                  <Divider sx={{ my: 1 }} />
                </div>
              )}

              {data.personal.urls?.length > 0 && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    URLs
                  </Typography>
                  <List dense>
                    {data.personal.urls.map((url, i) => (
                      <ListItem key={i} disablePadding>
                        <Link href={url} target="_blank" rel="noopener noreferrer">
                          {url}
                        </Link>
                      </ListItem>
                    ))}
                  </List>
                  <Divider sx={{ my: 1 }} />
                </>
              )}

              {data.personal.emails?.length > 0 && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    E-mails
                  </Typography>
                  <List dense>
                    {data.personal.emails.map((e, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemText primary={e} />
                      </ListItem>
                    ))}
                  </List>
                  <Divider sx={{ my: 1 }} />
                </>
              )}

              {data.personal.countries?.length > 0 && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    Países
                  </Typography>
                  <List dense>
                    {data.personal.countries.map((c, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemText primary={c} />
                      </ListItem>
                    ))}
                  </List>
                  <Divider sx={{ my: 1 }} />
                </>
              )}

              {data.personal.external_ids?.length > 0 && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    Identificadores externos
                  </Typography>
                  <List dense>
                    {data.personal.external_ids.map((ex, i) => (
                      <ListItem key={i} disablePadding>
                        <ListItemText primary={`${ex.type}: ${ex.value}`} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </>
          )}
        </Box>
      </StyledDrawer>
    </Box>
  );
}
