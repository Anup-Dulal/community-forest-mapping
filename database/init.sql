-- Create database if not exists
CREATE DATABASE cfm;

-- Connect to cfm database
\c cfm;

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Create schema
CREATE SCHEMA IF NOT EXISTS cfm;

-- Set search path
SET search_path TO cfm, public;

-- Create tables
\i schema.sql
