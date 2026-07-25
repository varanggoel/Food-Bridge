import { gql } from "@apollo/client";

export const GET_DONATIONS = gql`
  query GetDonations {
    donations {
      id
      restaurantName
      assignedNGO
      status
      emailSent
      createdAt
    }
  }
`;

export const GET_DONATION = gql`
  query GetDonation($id: String!) {
    donation(id: $id) {
      id
      restaurantName
      restaurantEmail
      restaurantPhone
      foodType
      quantity
      preparationTime
      pickupAddress
      city
      notes
      status
      assignedNGO
      ngoEmail
      aiReason
      emailSubject
      emailBody
      emailSent
      createdAt
    }
  }
`;

export const GET_NGOS = gql`
  query GetNGOs {
    ngos {
      id
      name
      email
      city
    }
  }
`;

export const CREATE_DONATION = gql`
  mutation CreateDonation($input: DonationInput!) {
    createDonation(input: $input) {
      success
      message
      donation {
        id
        status
        assignedNGO
        emailSent
      }
    }
  }
`;

export const CREATE_NGO = gql`
  mutation CreateNGO($input: NGOInput!) {
    createNGO(input: $input) {
      id
      name
      email
      city
    }
  }
`;

export const DELETE_NGO = gql`
  mutation DeleteNGO($id: String!) {
    deleteNGO(id: $id)
  }
`;

export const RESEND_EMAIL = gql`
  mutation ResendEmail($id: String!) {
    resendEmail(id: $id) {
      success
      message
      donation {
        id
        emailSent
      }
    }
  }
`;
